# Font-Generator

```sh
python ./main ..\\images\\test1-number ..\\fonts\\test1-number.ttf
```

## Requirements

To run this program, please install these requirements:

```
opencv-python
pillow
numpy
```

and these software:

### Potrace

unzip the package in `/potrace/installer`, and copy the executable file into `/potrace/bin`.

### FontForge

I really recommand using this program under Linux enviroment. It is inconvinient to use fontforge as a python extention under Windows. 

**update:**

change the method using fontforge to *ffpython*. 

Install fontforge under Windows, add it's bin fold's path into var *PATH*, and enjoy it!