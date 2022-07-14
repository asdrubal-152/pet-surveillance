from requests import get
from zipfile import ZipFile
from os import makedirs, listdir, remove
from shutil import move, copy, rmtree
from random import shuffle

from ..utils import paths



class DataDownload():
    # Paths

    def __init__(self) -> None:    
        self.file_name = "Unity_Residential_Interiors.zip"
        
        self.url_dataset_zip = "https://storage.googleapis.com/"\
                              +"computer-vision-datasets/"\
                              + f"residential/{self.file_name}"

        ## Zip related paths
        self.zip_destiny_path = self.__local_dir('tmp', self.file_name)
        self.unzip_path = self.__local_dir('tmp', self.file_name[:-4].lower())

        ## Paths to reorganize files within the project layout.
        self.dataset_path = self.__local_dir('data','raw',
                                             'semantic_segmentation',
                                             'unity_residential_interiors')

        ### Paths before moving.
        self.tmp_images_dir = self.unzip_path.joinpath(
            'Residential Interiors Dataset',
            'RGB2d9da855-d495-4bd9-9a1f-6744db5a3249')

        self.tmp_labels_dir = self.tmp_images_dir.parent.joinpath(
            'SemanticSegmentation50529ca2-588c-4aba-ab92-a9d4a31a56d4'
        )

        ### Paths after moving
        self.raw_images_dir = self.dataset_path.joinpath('images')
        self.raw_labels_dir = self.dataset_path.joinpath('labels')

        ## Path for train and validation sub sets.
        self.dataset_processed_path = self.__local_dir(
            'data','processed','semantic_segmentation',
            'unity_residential_interiors')

    def __local_dir(self, *args):
        local_dir = paths.make_dir_function()
        return local_dir(*args)


    def donwload_zip_file(self):
        if not self.zip_destiny_path.is_file():
            self.zip_destiny_path.parent.mkdir(exist_ok=True)
            response = get(self.url_dataset_zip, stream=True)

            with open(self.zip_destiny_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
            
            
            print(f"{self.file_name} has been downloaded!")
        
        else:
            print(f"{self.file_name} already existed!")


    def unzip_files(self):
        if not paths.is_valid(self.unzip_path):
            with ZipFile(self.zip_destiny_path, 'r') as zip_ref:
                zip_ref.extractall(self.unzip_path)
            
            print(f"{self.file_name} has been unzipped to the directory "\
                +f"{self.unzip_path.relative_to(self.__local_dir())}!")

        else:
            print("The directory "\
                +f"{self.unzip_path.relative_to(self.__local_dir())} already "\
                + "exists and isn't empty!")
                
        
    def move_files(self):
        makedirs(self.dataset_path, exist_ok=True)

        for source, destiny in zip([self.tmp_images_dir, self.tmp_labels_dir], 
                                [self.raw_images_dir, self.raw_labels_dir]):
        
            if not paths.is_valid(destiny):
                move(
                    src=source,
                    dst=destiny
                )

        
        print(f"The files have been moved or already exist.")


    def create_train_validation_names_list(self):
        file_names = [name[4:-4] 
                      for name in listdir(self.raw_images_dir) 
                      if name.endswith('.png')]
        shuffle(file_names)

        n_train = round(len(file_names)*0.7)

        train_names = file_names[:n_train]
        val_names = file_names[n_train:]

        return(train_names, val_names)

    def move_files_to_train_and_validation_folders(self):

        if paths.is_valid(self.dataset_processed_path):
            print("The directory "\
                +f"{self.dataset_processed_path.relative_to(self.__local_dir())}"\
                + " already existed and isn't empty!")
            
            return None
        

        train_names, val_names = self.create_train_validation_names_list()    
        self.dataset_processed_path.mkdir(parents=True, exist_ok=True)

        for set_name, file_names in zip(['train', 'val'], [train_names, val_names]):
            for set_type, name_prefix in zip(['images', 'labels'], 
                                            ['rgb', 'segmentation']):
                for file_name in file_names:
                    destiny_path = self.dataset_processed_path.joinpath(
                        f'{set_name}_{set_type}',
                        f'{file_name}.png'
                    )

                    origin_path = self.dataset_path.joinpath(
                        set_type, f'{name_prefix}_{file_name}.png'
                    )

                    if not destiny_path.parent.is_dir():
                        destiny_path.parent.mkdir(exist_ok=True)

                    copy(origin_path, destiny_path)


    def start(self, overwrite=False):
        if overwrite:
            if self.zip_destiny_path.is_file():
                remove(self.zip_destiny_path)

            for path in [self.unzip_path, self.dataset_path, 
                         self.dataset_processed_path]:
                if path.is_dir():
                    rmtree(path)
             
        self.donwload_zip_file()
        self.unzip_files()
        self.move_files()
        self.move_files_to_train_and_validation_folders()









