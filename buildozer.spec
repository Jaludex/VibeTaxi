[app]

# (str) Title of your application
title = Vibe Taxi

# (str) Package name
package.name = vibetaxi

# (str) Package domain (needed for android/ios packaging)
package.domain = org.whiteboxstudio

# (str) Source code where the main.py lives
source.dir = vibetaxi

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,ttf,wav,ogg,mp3,json,sav,ico,icns

# (list) List of directory to exclude (leave empty to not exclude anything)
source.exclude_dirs = dist,build,__pycache__,saves

# (str) Application versioning
version = 1.5.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame,numpy,cffi,pycparser,click,pymunk,gale-engine,pyinstance

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/graphics/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse, landscape-reverse, or all
orientation = landscape

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (string) Presplash background color (for android toolchain)
android.presplash_color = #111111

# (list) Permissions
android.permissions = INTERNET,VIBRATE

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 24

# (str) Android NDK directory
android.ndk_path = /home/Jaludex/.buildozer/android/platform/android-ndk-r28c

# (str) Android SDK directory
android.sdk_path = /home/Jaludex/.buildozer/android/platform/android-sdk

# (bool) If True, then skip trying to update the Android SDK
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

# (list) Android application meta-data to set (key=value format)
android.meta_data = android.max_aspect=2.5

#
# Python for android (p4a) specific
#

# (str) python-for-android git clone directory
p4a.source_dir = /home/Jaludex/.buildozer/android/platform/python-for-android

# (str) The directory in which python-for-android should look for your own build recipes (if any)
p4a.local_recipes = ./p4a-recipes

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
