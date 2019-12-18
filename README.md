# YSE_PZ_photo_Z

download, place Photo_Z in data_digest.py

place model in some logical place, and then change 'path_to_model' inside to match, remember that I developed in windows so change the path strings to Unix from Dos: \\ -> /

Add 'YSE_App.data_ingest.Photo_Z.YSE' to settings.py file under Cron

Install dependencies: Scikit-learn, and this: https://github.com/sciserver/SciScript-Python which has broken(???) pip install, but luckily the git manual install works fine for me

grab the model from here: https://drive.google.com/drive/folders/1dl1SueUpUQ_2RcuevS_HaX6zRH9GGKUQ?usp=sharing


What I know needs fixing:

1) Something along the lines of Transients.objects.filter(photometric_redshift=None & tags.galactic_host=True) should be how we find transients to give photometric redshifts.

2) Don't know how to upload back to the server

3) if file is over 1000, then batch it and piece it back together b/c CAS server has a limited number of lines... or rather whatever dumb way I am using it does

4) This can only grab redshifts for things that are in the SDSS footprint, if it isn't need to learn how to query the information from Pan-Starrs and create a new/seperate/better model to deal with missing u-band information. Which we think makes the problem much harder.

5) In general I am working on a CNN solution to redshifts and will want to implement that anyways. Dealing with partial information is tough though.

6) SDSS query grabs nearest thing inside ### arcseconds so if astrometry is off, or rather, different than SDSS, this will fail. or if another object is closer to that it will grab the wrong data. not good.

5) General improvements, what can I vectorize yada yada
