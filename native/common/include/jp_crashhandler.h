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
#ifndef JP_CRASHHANDLER_H
#define JP_CRASHHANDLER_H

#include <string>
#include <vector>
#include <iostream>
#include <sstream>

/**
 * Crash Handler for JPype
 *
 * Provides comprehensive crash diagnostics including:
 * - C++ stack trace with symbol resolution
 * - Python stack trace with source lines
 * - Java stack trace (if available)
 *
 * This handler is called when fatal exceptions occur that cannot be
 * recovered through normal exception handling mechanisms.
 */

struct JPCrashInfo
{
	std::string cppStackTrace;
	std::string pythonStackTrace;
	std::string javaStackTrace;
	std::string errorMessage;
	int errorCode;
};

class JPCrashHandler
{
public:
	/**
	 * Initialize the crash handler with signal handlers.
	 * Should be called during JPype initialization.
	 */
	static void initialize();

	/**
	 * Get the C++ stack trace with symbol resolution.
	 * Each line includes the memory address and function name.
	 *
	 * @param maxFrames Maximum number of frames to capture (0 = unlimited)
	 * @return String containing the formatted stack trace
	 */
	static std::string getCppStackTrace(int maxFrames = 32);

	/**
	 * Get the Python stack trace with file:line information and source code.
	 * Requires an active Python interpreter.
	 *
	 * @return String containing the formatted Python traceback
	 */
	static std::string getPythonStackTrace();

	/**
	 * Get the Java stack trace from the current thread's exception.
	 * Should only be called when a Java exception is active.
	 *
	 * @param env JNI environment (optional, will be obtained if null)
	 * @return String containing the formatted Java stack trace
	 */
	static std::string getJavaStackTrace(JNIEnv* env = nullptr);

	/**
	 * Capture a complete crash report with all available information.
	 *
	 * @param errorMsg Description of what caused the crash
	 * @param errorCode Error code if applicable
	 * @return JPCrashInfo structure containing all diagnostic information
	 */
	static JPCrashInfo captureCrashInfo(const std::string& errorMsg = "", int errorCode = -1);

	/**
	 * Print the crash report to stderr.
	 * This is called automatically by signal handlers.
	 *
	 * @param info The crash information to print
	 */
	static void printCrashReport(const JPCrashInfo& info);

	/**
	 * Emergency signal handler that captures crash info and exits gracefully.
	 * Called on SIGSEGV, SIGABRT, SIGBUS, etc.
	 *
	 * @param signum Signal number
	 */
	static void emergencyHandler(int signum);

	/**
	 * Set a custom callback to be invoked when a crash is detected.
	 * Allows for custom logging, telemetry, or cleanup.
	 *
	 * @param callback Function to call with crash info
	 */
	typedef void (*CrashCallback)(const JPCrashInfo& info);
	static void setCustomCallback(CrashCallback callback);

	/**
	 * Disable automatic signal handler registration.
	 * Useful for testing or when JPype is embedded in another system.
	 */
	static void disableSignalHandlers();

private:
	static bool s_signalHandlersEnabled;
	static CrashCallback s_customCallback;
	
	// Internal helper for symbol resolution
	static std::string demangleSymbol(const char* symbol);
};

#endif // JP_CRASHHANDLER_H
