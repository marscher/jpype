/*****************************************************************************
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

		http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   See NOTICE file for details.
 *****************************************************************************/
#include <Python.h>
#include <frameobject.h>

#include <signal.h>
#include <iomanip>
#include <cxxabi.h>
#include <dlfcn.h>
#include <execinfo.h>
#include <sstream>
#include <cstring>

#include "jpype.h"
#include "jp_crashhandler.h"
#include "pyjp.h"

// Static members
bool JPCrashHandler::s_signalHandlersEnabled = true;
JPCrashHandler::CrashCallback JPCrashHandler::s_customCallback = nullptr;

// Store previous handlers for chaining
static struct sigaction s_prevSigSEGV;
static struct sigaction s_prevSigABRT;
static struct sigaction s_prevSigBUS;

std::string JPCrashHandler::demangleSymbol(const char* symbol)
{
	int status = 0;
	char* demangled = abi::__cxa_demangle(symbol, nullptr, nullptr, &status);
	
	if (status == 0)
	{
		std::string result(demangled);
		free(demangled);
		return result;
	}
	
	// If demangling fails, return the original symbol
	return std::string(symbol);
}

std::string JPCrashHandler::getCppStackTrace(int maxFrames)
{
	const int BUFFER_SIZE = 256;
	void* addrlist[BUFFER_SIZE];
	
	// Capture the stack trace
	int frames = backtrace(addrlist, maxFrames > 0 ? maxFrames : BUFFER_SIZE);
	char** symbols = backtrace_symbols(addrlist, frames);
	
	std::ostringstream oss;
	oss << "\n=== C++ Stack Trace ===\n";
	oss << "Frames: " << frames << "\n\n";
	
	for (int i = 0; i < frames; i++)
	{
		Dl_info info;
		if (dladdr(addrlist[i], &info) && info.dli_sname)
		{
			std::string demangled = demangleSymbol(info.dli_sname);
			oss << "[" << i << "] " << info.dli_fname << " : " 
				<< demangled << " + 0x" 
				<< std::hex << (uintptr_t)addrlist[i] - (uintptr_t)info.dli_saddr
				<< std::dec << "\n";
		}
		else
		{
			// Fallback to raw symbol
			oss << "[" << i << "] " << symbols[i] << "\n";
		}
	}
	
	free(symbols);
	oss << "\n";
	return oss.str();
}

std::string JPCrashHandler::getPythonStackTrace()
{
	std::ostringstream oss;
	oss << "\n=== Python Stack Trace ===\n";
	
	try
	{
		// Get the current Python frame
		PyObject* globals = PyEval_GetGlobals();
		if (!globals)
		{
			oss << "No Python traceback available (not in Python thread)\n\n";
			return oss.str();
		}
		
		// Get the current exception
		PyObject *ptype, *pvalue, *ptraceback;
		PyErr_Fetch(&ptype, &pvalue, &ptraceback);
		
		if (ptraceback)
		{
			PyTracebackObject* tb = (PyTracebackObject*) ptraceback;
			int frameNum = 0;
			
			while (tb != nullptr)
			{
				PyFrameObject* frame = tb->tb_frame;
				int lineno = PyTracebackObject_lasti(tb);
				
				if (!lineno)
					lineno = frame->f_lineno;
				
				// File name
				const char* filename = PyUnicode_AsUTF8(frame->f_code->co_filename);
				if (!filename) filename = "<unknown>";
				
				// Function name
				const char* funcname = PyUnicode_AsUTF8(frame->f_code->co_name);
				if (!funcname) funcname = "<unknown>";
				
				oss << "  File \"" << filename << "\", line " << lineno
					<< ", in " << funcname << "\n";
				
				// Try to get source line
				PyObject* linecache = PyImport_ImportModule("linecache");
				if (linecache)
				{
					PyObject* line = PyObject_CallMethod(
						linecache, "getline", "sI",
						filename, lineno
					);
					if (line && PyUnicode_Check(line))
					{
						const char* linestr = PyUnicode_AsUTF8(line);
						if (linestr)
						{
							// Strip and show the first 80 chars
							std::string trimmed(linestr);
							size_t start = trimmed.find_first_not_of(" \t\n\r");
							if (start != std::string::npos)
								trimmed = trimmed.substr(start);
							if (trimmed.length() > 80)
								trimmed = trimmed.substr(0, 77) + "...";
							oss << "    " << trimmed << "\n";
						}
						Py_DECREF(line);
					}
					Py_DECREF(linecache);
				}
				
				tb = tb->tb_next;
				frameNum++;
			}
			
			// Print exception message
			if (pvalue)
			{
				PyObject* exc_str = PyObject_Str(pvalue);
				if (exc_str)
				{
					const char* exc_msg = PyUnicode_AsUTF8(exc_str);
					if (exc_msg)
						oss << "\nException: " << exc_msg << "\n";
					Py_DECREF(exc_str);
				}
			}
			
			// Restore the exception
			PyErr_Restore(ptype, pvalue, ptraceback);
		}
		else
		{
			// Restore if needed
			PyErr_Restore(ptype, pvalue, ptraceback);
			oss << "No active Python exception\n";
		}
	}
	catch (...)
	{
		oss << "Error while capturing Python stack trace\n";
	}
	
	oss << "\n";
	return oss.str();
}

std::string JPCrashHandler::getJavaStackTrace(JNIEnv* env)
{
	std::ostringstream oss;
	oss << "\n=== Java Stack Trace ===\n";
	
	try
	{
		// Try to get the environment if not provided
		if (!env)
		{
			// This is a best-effort attempt - we can't safely get the environment
			// from a signal handler without causing additional crashes
			oss << "JNI environment not available in crash context\n";
			return oss.str();
		}
		
		// Check if there's a current exception
		jthrowable exception = env->ExceptionOccurred();
		if (!exception)
		{
			oss << "No active Java exception\n\n";
			return oss.str();
		}
		
		// Get the Throwable class
		jclass throwableClass = env->FindClass("java/lang/Throwable");
		if (!throwableClass)
		{
			oss << "Could not find Throwable class\n\n";
			return oss.str();
		}
		
		// Get toString method
		jmethodID toStringMethod = env->GetMethodID(
			throwableClass, "toString", "()Ljava/lang/String;"
		);
		if (!toStringMethod)
		{
			oss << "Could not find toString method\n\n";
			return oss.str();
		}
		
		// Get the exception message
		jobject excStr = env->CallObjectMethod(exception, toStringMethod);
		if (excStr)
		{
			const char* excMsg = env->GetStringUTFChars((jstring)excStr, nullptr);
			oss << excMsg << "\n\n";
			env->ReleaseStringUTFChars((jstring)excStr, excMsg);
			env->DeleteLocalRef(excStr);
		}
		
		// Get getStackTrace method
		jmethodID getStackTraceMethod = env->GetMethodID(
			throwableClass, "getStackTrace", "()[Ljava/lang/StackTraceElement;"
		);
		if (getStackTraceMethod)
		{
			jobjectArray stackTrace = (jobjectArray)env->CallObjectMethod(
				exception, getStackTraceMethod
			);
			
			if (stackTrace)
			{
				jint length = env->GetArrayLength(stackTrace);
				jclass stackTraceElementClass = env->FindClass(
					"java/lang/StackTraceElement"
				);
				
				jmethodID toStringSTEMethod = env->GetMethodID(
					stackTraceElementClass, "toString", "()Ljava/lang/String;"
				);
				
				for (jint i = 0; i < length && i < 50; i++)  // Limit to 50 frames
				{
					jobject element = env->GetObjectArrayElement(stackTrace, i);
					jobject elementStr = env->CallObjectMethod(element, toStringSTEMethod);
					
					if (elementStr)
					{
						const char* elementMsg = env->GetStringUTFChars((jstring)elementStr, nullptr);
						oss << "  at " << elementMsg << "\n";
						env->ReleaseStringUTFChars((jstring)elementStr, elementMsg);
						env->DeleteLocalRef(elementStr);
					}
					
					env->DeleteLocalRef(element);
				}
				
				env->DeleteLocalRef(stackTrace);
			}
		}
		
		env->DeleteLocalRef(throwableClass);
	}
	catch (...)
	{
		oss << "Error while capturing Java stack trace\n";
	}
	
	oss << "\n";
	return oss.str();
}

JPCrashInfo JPCrashHandler::captureCrashInfo(const std::string& errorMsg, int errorCode)
{
	JPCrashInfo info;
	info.errorMessage = errorMsg;
	info.errorCode = errorCode;
	
	// Capture C++ stack trace
	info.cppStackTrace = getCppStackTrace();
	
	// Capture Python stack trace if we're in a Python thread
	if (PyGILState_Check())
	{
		info.pythonStackTrace = getPythonStackTrace();
	}
	
	// Java stack trace must be captured outside of signal handlers
	// It will be captured separately if needed
	info.javaStackTrace = "\n=== Java Stack Trace ===\nCannot safely capture from crash context\n\n";
	
	return info;
}

void JPCrashHandler::printCrashReport(const JPCrashInfo& info)
{
	std::cerr << "\n";
	std::cerr << "========================================\n";
	std::cerr << "JPYPE CRASH REPORT\n";
	std::cerr << "========================================\n";
	
	if (!info.errorMessage.empty())
	{
		std::cerr << "Error: " << info.errorMessage << "\n";
	}
	
	if (info.errorCode != -1)
	{
		std::cerr << "Error Code: " << info.errorCode << "\n";
	}
	
	std::cerr << info.cppStackTrace;
	std::cerr << info.pythonStackTrace;
	std::cerr << info.javaStackTrace;
	
	std::cerr << "========================================\n";
	std::cerr << "Please report this crash at:\n";
	std::cerr << "https://github.com/jpype-project/jpype/issues\n";
	std::cerr << "========================================\n\n";
	
	std::cerr.flush();
}

void JPCrashHandler::emergencyHandler(int signum)
{
	const char* signal_name = "UNKNOWN";
	switch (signum) {
		case SIGSEGV: signal_name = "SIGSEGV (Segmentation Fault)"; break;
		case SIGABRT: signal_name = "SIGABRT (Abort)"; break;
		case SIGBUS:  signal_name = "SIGBUS (Bus Error)"; break;
		case SIGFPE:  signal_name = "SIGFPE (Floating Point Exception)"; break;
		case SIGILL:  signal_name = "SIGILL (Illegal Instruction)"; break;
	}
	
	JPCrashInfo info = captureCrashInfo(signal_name, signum);
	printCrashReport(info);
	
	if (s_customCallback)
	{
		try {
			s_customCallback(info);
		} catch (...) {
			// Ignore exceptions during callback
		}
	}
	
	// Exit with non-zero status
	_exit(128 + signum);
}

static void emergency_signal_handler(int signum)
{
	JPCrashHandler::emergencyHandler(signum);
}

void JPCrashHandler::initialize()
{
	if (!s_signalHandlersEnabled)
		return;
	
	struct sigaction action;
	memset(&action, 0, sizeof(action));
	action.sa_handler = emergency_signal_handler;
	sigemptyset(&action.sa_mask);
	action.sa_flags = 0;
	
	// Register handlers for common fatal signals
	// Note: We save previous handlers but don't chain them for now
	// This could be enhanced to call previous handlers if needed
	sigaction(SIGSEGV, &action, &s_prevSigSEGV);
	sigaction(SIGABRT, &action, &s_prevSigABRT);
	sigaction(SIGBUS,  &action, &s_prevSigBUS);
}

void JPCrashHandler::setCustomCallback(CrashCallback callback)
{
	s_customCallback = callback;
}

void JPCrashHandler::disableSignalHandlers()
{
	s_signalHandlersEnabled = false;
}
