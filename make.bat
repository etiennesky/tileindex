# this make script sent by François Lambert (untested by plugin author)

@echo off

SET OSGEO4W_ROOT=C:\QGIS
call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
call "%OSGEO4W_ROOT%"\apps\grass\grass-6.4.2\etc\env.bat
SET GDAL_DRIVER_PATH=%OSGEO4W_ROOT%\bin\gdalplugins\1.8
path %PATH%;%OSGEO4W_ROOT%\apps\qgis\bin;%OSGEO4W_ROOT%\apps\grass\grass-6.4.2\lib

pyrcc4 -o resources_rc.py resources.qrc
python "C:\QGIS\apps\Python27\Lib\site-packages\PyQt4\uic\pyuic.py" -o ui_tileindex.py -x ui_tileindex.ui
python "C:\QGIS\apps\Python27\Lib\site-packages\PyQt4\uic\pyuic.py" -o ui_tileindexrenderwidgetbase.py -x ui_tileindexrenderwidgetbase.ui