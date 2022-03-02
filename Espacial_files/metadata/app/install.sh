#sudo add-apt-repository ppa:ubuntugis/ppa && sudo apt-get update
#sudo apt-get update

sudo apt-get install libpq5=12.5-0ubuntu0.20.04.1
sudo apt-get install gdal-bin
sudo apt-get install libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL
