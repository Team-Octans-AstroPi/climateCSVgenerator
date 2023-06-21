# ClimateCSVgenerator
This repository includes a few scripts that were used to generate the climate CSV dataset for training our climate classification model.

## Data from <picture><source media="(prefers-color-scheme: dark)" srcset="https://weatherkit.apple.com/assets/branding/en/Apple_Weather_wht_en_3X_090122.png"><source media="(prefers-color-scheme: light)" srcset="https://weatherkit.apple.com/assets/branding/en/Apple_Weather_blk_en_3X_090122.png"><img src="" height="18" alt="Apple Weather Logo"></picture>
The code in this repository uses data from Apple Weather, that may be modified and used for training the ML model in other repositories.
Data sources attribution: https://developer.apple.com/weatherkit/data-source-attribution/.

## Data from climateapi.scottpinkelman.com
The code in this repository uses data from http://climateapi.scottpinkelman.com.
It uses data from the Institute for Veterinary Public Health and the Provincial Government of Carinthia in Austria.

<b>Citation:</b><br>
Kottek, M., J. Grieser, C. Beck, B. Rudolf, and F. Rubel, 2006: World Map of the Köppen-Geiger climate classification updated. Meteorol. Z., 15, 259-263. DOI: 10.1127/0941-2948/2006/0130.

## Content description:
- `ndvi_weatherkit.py` is the main code. This cycles through all the images and gets location and time data. Then, it uses which computes plant health as in imageSeparationCV2, gets the climate
- `getcloudinfo.py` and `getlandinfo.py`
