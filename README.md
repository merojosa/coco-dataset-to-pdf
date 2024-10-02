# COCO dataset to PDF

- Initiate a [virtual environment](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/):

```
python -m venv coco-dataset-pdf-visualizer-env
coco-dataset-pdf-visualizer-env/Scripts/activate.bat
```

Windows: 
```
coco-dataset-pdf-visualizer-env/Scripts/activate.bat
```

MacOS: 
```
source ./coco-dataset-pdf-visualizer-env/bin/activate
```

- Install the dependencies: `pip install -r requirements.txt`

- Add `dataset` folder to the root of the project with its respective `_annotations.coco.json` and the images.

- Execute the script: `python main.py`

- A `result.pdf` file will be generated
