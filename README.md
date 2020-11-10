# AnieZillaProject

Client for uploading .mp4 files to an ftp server and registering the file's metadata in a MySql database.

Unfortunately, the website on which it was previously being used is no longer live, but I believe that this project can be a precursor to several others to come.

It was built entirely upon Python3 and it is using tkinter for the UI (I know, I know). It is **__NOT__** a professional project, that's why you might find a messy and cluttered code, it was being made while I was learning python (I'm still learning, but I'm a lot better, I hope), so, take it easy.

The main thing it does is upload of .mp4 files (and .png images) to an FTP server and, secondly, but not less important, it records the file's metadata in a [MySql](https://www.mysql.com/) database.

### Other interesting things that it does are:
- Craws the [Crunchyroll](https://www.crunchyroll.com/pt-br) website for anime information like the show's name, episode's names, seasons, and many other things. To do that, it uses the beautifulsoup4 library.
- Uses [FFmpeg](https://ffmpeg.org/) to extract some metadata like the length of the episode and dimensions (width and height).

It was being used primarily by uploaders in the [anieclipse.tk](http://anieclipse.tk) website to upload anime episodes to be watched online.

You can try to build it, or you can simply download the most updated release available, but I don't see a point to that, maybe this code will be better used to take something useful from it or try to build something from it.

### Anyway, to built it, you are going to need to install:
 - [tkinter](https://docs.python.org/3/library/tkinter.html).
 - [bcrypt](https://pypi.org/project/bcrypt/).
 - [beautifulsoup4](https://pypi.org/project/beautifulsoup4/).
 - [pymysql](https://pypi.org/project/PyMySQL/).
 - [PyInstaller](https://www.pyinstaller.org/).
 - [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/).
