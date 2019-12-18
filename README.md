# YSE_PZ_photo_Z

download, place Photo_Z in data_digest.py

place model in some logical place, and then change 'path_to_model' inside to match, remember that I developed in windows so change the path strings to Unix from Dos: \\ -> /

Add 'YSE_App.data_ingest.Photo_Z.YSE' to settings.py file under Cron

Install dependencies: Scikit-learn, and this: https://github.com/sciserver/SciScript-Python which has broken(???) pip install, but luckily the git manual install works fine for me
