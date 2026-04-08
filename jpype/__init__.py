# *****************************************************************************
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   See NOTICE file for details.
#
# *****************************************************************************
import _jpype
from ._jinit import onJVMStart
from ._jpackage import JPackage
from ._jproxy import JProxy, JImplements
from ._core import (
    isJVMStarted, startJVM, shutdownJVM,
    getDefaultJVMPath, getJVMVersion,
    isThreadAttachedToJVM, attachThreadToJVM,
    detachThreadFromJVM, synchronized,
    JVMNotFoundException, JVMNotSupportedException,
    JVMNotRunning
)
from ._gui import setupGuiEnvironment, shutdownGuiEnvironment
from ._classpath import addClassPath, getClassPath
from ._jclass import JClass, JInterface, JOverride
from .types import (
    JArray, JBoolean, JByte, JChar, JShort,
    JInt, JLong, JFloat, JDouble, JString, JObject, JException
)
from ._jcustomizer import JImplementationFor, JConversion
from . import nio
from . import types
# Import all the class customizers
# Customizers are applied in the order that they are defined currently.
from . import _jmethod # noqa: F401
from . import _jcollection # noqa: F401
from . import _jio # noqa: F401
from . import protocol # noqa: F401
from . import _jthread # noqa: F401

__all__ = [
    'onJVMStart',
    # core:
    'isJVMStarted', 'startJVM', 'shutdownJVM',
    'getDefaultJVMPath', 'getJVMVersion',
    'isThreadAttachedToJVM', 'attachThreadToJVM',
    'detachThreadFromJVM', 'synchronized',
    'JVMNotFoundException', 'JVMNotSupportedException', 'JVMNotRunning',
    # gui:
    'setupGuiEnvironment', 'shutdownGuiEnvironment',
    # classpath:
    'addClassPath', 'getClassPath',
    # jclass:
    'JClass', 'JInterface', 'JOverride',
    # types:
    'JArray', 'JBoolean', 'JByte', 'JChar', 'JShort',
    'JInt', 'JLong', 'JFloat', 'JDouble', 'JString', 'JObject', 'JException',
    # protocol:
    'JImplementationFor', 'JConversion',
    'JProxy', 'JImplements',
    'JPackage',
    # modules:
    'protocol', 'nio', 'types',
    'java', 'javax',
]

__version__ = "1.6.1.dev0"
__version_info__ = __version__.split('.')

# FIXME these should be deprecated. The old JPackage system is only for
#  python2 series and generates lots of deceptive classes.  At some point
#  these two are going to have to go away.
java = JPackage("java", strict=True)
javax = JPackage("javax", strict=True)
# todo: try to replace them with the modern system.

JMethod = _jpype._JMethod
JField = _jpype._JField

if hasattr(_jpype, 'bootstrap'):
    _jpype.bootstrap()
    from jpype import _core
    _core.initializeResources()
    del _core
