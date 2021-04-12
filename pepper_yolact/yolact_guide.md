## How to train and test Yolact (taken from crow_simulation)

All what is needed for evaluation and inference is in the yolact_vision folder in ciircgym repository. For training, crow_vision_yolact repository needs to be cloned next to the ciircgym repository.

[Google spreadsheet with the Yolact training log](https://docs.google.com/spreadsheets/d/1e2cF4o-m6uzBkcgg43tZrHf4xXqADsjuNAoRJNmynaY/edit?usp=sharing) Notes on dataset structure and trained net performance. All datasets and weights are to be found on cluster.

#### Generate dataset 

In COCO format:
`python generate_dataset.py configs/config_coco.json` 
 fills output_folder set in config_coco.json with images in correct format. See example config 'config_coco.json' for details about options, including randomization settings.

 `merge_coco_annotations.py --dir=path_to_dataset.../train/ --clean-files`
 `merge_coco_annotations.py --dir=path_to_dataset.../test/ --clean-files`

 The dataset config is saved into generated dataset folder for info and later use in traning stage. Do not use git tags anymore.

Note: Do not include background class: "During eval, the network predicts the number of classes + 1 (the extra class in the config) and softmax over that dimension. After that, we just cut out that extra class and return that as the class predictions."

#### Training
The source code including environment.yml file is in repo crow_vision_yolact, branch master

`python train.py` (default: yolact_base_config, batch_size=8)  
`python train.py --config=yolact_base_config --batch_size=5` (changing arguments)
`python train.py --dataset_number=xy` loads dataset config from folder '.../data/yolact/datasets/dataset_kuka_env_pybullet_xy' and edit the training config for you to train on the xy dataset
`python train.py --resume=../data/yolact/weights/weights_yolact_kuka_4/yolact_base_1136_100000.pth --start_iter=-1` (resume from the iter in the pth file name, training runs until max_iter (in config.py) is reached).

If you log your stdout during training:  
`python train.py > train_log.log`  
you can plot the train loss:  
`python -m "scripts.plot_loss" train_log.log`  
and mAP over iteration:  
`python -m "scripts.plot_loss" train_log.log val`

Multi GPU (grid):  
`export CUDA_VISIBLE_DEVICES=gpu1_nr,gpu2_nr`  
`python train.py ---batch_size=8*num_gpus`  
Note: do not use this format [gpu1_nr,gpu2_nr].

Cluster (slurm) training:
Example *train_cluster.sh* script to be found in crow_vision repo.

### Hyperparameters to tune:  
lr_steps, max_iter at the end of config.py  
(example: lr_steps=(70000, 150000, 175000, 187500), max_iter=200000, lr starts at 0.001 and is multiplied by gamma=0.1 each time next lr_step iteration is achieved)
One iter == training on one batch of images. One episode = training on all the training data. (example: 3200 images in dataset/train, max_iter = 200000 --> 400 iterations in each epoch, 500 epochs in total. Each 1000 iterations = cca 10 mins with 1 GPU and batch_size=8)  
pred_aspect_ratios and pred_scales. Check yolact_base_config for details.

Note: (problem to recognize small objects) If you want to still use 300x300, I'd halve all of the anchor sizes in "pred_scales" (in yolact_base). Also if you want to train the model to use 300x300 images, set max_size to 300.

### GPU memory 
training batch_size=8 --> 12 GB (resolution 640x480)
inference --> 1.5 GB (resolution 640x480)

### mAP - mean average precision
upper row - IoU (intersection over union) treshold  
lower rows - mAP for boxes and masks  

currently showing this table for each class and individually and all classes together

|        |  all  |  .50  |  .55  |  .60  |  .65  |  .70  |  .75  |  .80  |  .85  |  .90  |  .95  |
|--------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
|   box  |  9.87 | 18.91 | 18.91 | 18.90 | 18.61 | 15.46 |  7.58 |  0.29 |  0.02 |  0.02 |  0.02 |
|  mask  |  5.65 | 18.29 | 18.29 | 14.05 |  5.87 |  0.00 |  0.00 |  0.00 |  0.00 |  0.00 |  0.00 |

More about mAP calculation in APDataObject in eval.py (line 513)
### Loss Key:
B: Box Localization Loss  
C: Class Confidence Loss  
M: Mask Loss  
P: Prototype Loss  
D: Coefficient Diversity Loss  
E: Class Existence Loss  
S: Semantic Segmentation Loss  
(T: Total)  

Loss types to be found in yolact/layers/modules/multibox_loss.py.

#### Evaluation 
On the fly using class *InfTool*, example usage in *test_environment_pybullet_yolact.py*: Two outputs: *"raw" classes, scores, boxes, masks* and *evaluated img with all masks, boxes, scores and class labels* that is visualized.
* Copy the weights from cluster, including config_train.obj file.  
* Set the path to the trained_model (weights) and corresponding config file.
* For older data: (Checkout git tag matching the weights you want to test according to the [Google spreadsheet with the Yolact training log](https://docs.google.com/spreadsheets/d/1e2cF4o-m6uzBkcgg43tZrHf4xXqADsjuNAoRJNmynaY/edit?usp=sharing). (The config.py in yolact/data has to match the one used during training, otherwise the evaluation crashes (size mismatch)).)


On a folder of images:  
`python eval.py --trained_model=../data/yolact/weights/weights_yolact_kuka_6/yolact_base_59_200000.pth --score_threshold=0.15 --top_k=15 --images=../data/yolact/datasets/dataset_kuka_env_pybullet_6/test:../data/yolact/datasets/dataset_kuka_env_pybullet_7/eval`  


On a test dataset: Uses the annotations of the test dataset and returns calculated mAP table (as it does during training). The kuka_env_pybullet_dataset_test is defined in config.py.   
`python eval.py --trained_model=../data/yolact/weights/weights_yolact_kuka_6/yolact_base_59_200000.pth --score_threshold=0.15 --top_k=15 --dataset=kuka_env_pybullet_dataset_test --max_images=1000`


On a video file: Saves annotated out.mp4 video to result.mp4
`python eval.py --trained_model=data/yolact/weights/crow_base_29_100000.pth --score_threshold=0.50 --top_k=15 --video_multiframe=4 --video=../Documents/real/out.mp4:result.mp4`

How to prepare video using RealSense camera: 
* `realsense-viewer` Open RealSense GUI, set parameters (camera resolution) and record video (bag format). Log in RealSense Viewer shows path to the bag file.
* `cd where_the_bag_file_is`
* `rs-convert -i 20200709_100405.bag -c -p real/crow_ ` Converts bag file to pngs in folder real with prep crow_
* `cd real`
* `ffmpeg -framerate 25 -pattern_type glob -i '*.png'   -c:v libx264 -r 30 -pix_fmt yuv420p out.mp4` Creates out.mp4 file from all pngs in folder

Note: if you need "raw" inference data (masks, bboxes etc.) for further post processing, use first evaluation method - *raw_inference* in *InfTool*. This method takes images as input. If you want to annotate a video file, use ffmpeg or similar tool to convert it to a folder of pngs first.

How to convert video to a folder of images:
`ffmpeg -i result.mp4 ./png_from_result/res_%05d.png`
