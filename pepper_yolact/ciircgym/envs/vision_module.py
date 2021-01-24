try:
    import torch
except:
    print("Torch doesn't work")
import sys
import numpy as np
import cv2

import pkg_resources
currentdir = pkg_resources.resource_filename("ciircgym", "envs")

# import YOLACT
sys.path.append(pkg_resources.resource_filename("ciircgym", "yolact_vision")) #may be moved somewhere else
try:
    #from yolact.inference_tool import InfTool
    from inference_tool import InfTool
except:
    print("Problem importing InfTool, humble yourself  ¯\_(ツ)_/¯")
try:
    from ciircgym.vae.helpers import load_checkpoint
except:
    print("Problem importing VAE, please tell Gabi")


class VisionModule:
    """Class that returns information from environment based on a visual subsystem (YOLACT, DOPE, VAE) or ground truth
    init arguments:
        - vision_src: str (ground_truth/vae/yolact/dope)
        - env: Env object (only needed for ground_truth case)
    """

    def __init__(self, vision_src="ground_truth", env=None):
        self.src = vision_src
        self.env = env
        self.vae_embedder = None
        self._initialize_network(self.src)
        self.mask = {}
        self.centroid = {}
        self.centroid_transformed = {}

    def get_module_type(self):
        return self.src

    def crop_image(self, img):
        dim1 = img.shape[0]
        crop1 = [int(dim1/4), int(dim1-(dim1/4))]
        dim2 = img.shape[1]
        crop2 = [int(dim2/4), int(dim2-(dim2/4))]
        img = img[crop1[0]:crop1[1], crop2[0]:crop2[1]]
        return img

    def get_obj_pixel_position(self, obj=None, img=None):
        """This might return a mask or object centroid from 2D image"""
        if self.src == "ground_truth":
            pass
            # @TODO mask, centroid
        elif self.src in ["dope", "yolact"]:
            if img is not None:
                #img = self.crop_image(img)
                if self.src == "yolact":
                    #obj="name" e.g. "cube_holes" defined in task.py
                    classes, class_names, scores, boxes, masks, centroids = self.inference_yolact(img)
                    # img_numpy = self.yolact_cnn.label_image(img)
                    # cv2.imshow("yolact inference", img_numpy)
                    # cv2.waitKey(1)
                    try:
                        self.mask[obj.get_name()] = masks[class_names.index(obj.get_name())]
                        self.centroid[obj.get_name()] = centroids[class_names.index(obj.get_name())]
                        #print("{} was detected".format(obj.get_name()))
                    except:
                        if obj.get_name() not in self.mask.keys():
                            self.mask[obj.get_name()] = [[-1]]
                            self.centroid[obj.get_name()] = [-1,-1]
                        #print("{} not detected in present image".format(obj.get_name()))

                    return self.mask[obj.get_name()], self.centroid[obj.get_name()]
                elif self.src == "dope":
                    pass
                    # @TODO
            else:
                raise Exception("You need to provide image argument for bbox segmentation")

    def get_obj_bbox(self, obj=None, img=None):
        # @TODO
        if self.src == "ground_truth":
            if obj is not None:
                return obj.get_bounding_box()
            else:
                raise Exception("You need to provide obj argument to get gt bounding box")
        elif self.src in ["dope", "yolact"]:
            if img is not None:
                if self.src == "yolact":
                    #obj="name" e.g. "cube_holes" defined in task.py
                    classes, class_names, scores, boxes, masks, centroids = self.inference_yolact(img)
                    try:
                        bbox = boxes[class_names.index(obj.get_name())]
                    except:
                        bbox = []
                        print("Object not detected in present image")
                    return bbox
                elif self.src == "dope":
                    pass
                    # @TODO
            else:
                raise Exception("You need to provide image argument for bbox segmentation")
        else:
            raise Exception("{} module does not provide bounding boxes!".format(self.src))

    def get_obj_position(self, obj=None, img=None, depth=None):
        """Returns object position in world coordinates"""
        # @TODO Do we want camera or world coordinates?
        if self.src == "ground_truth":
            if obj is not None:
                return list(obj.get_position())
            else:
                raise Exception("You need to provide obj argument to get gt position")
        elif self.src in ["yolact", "dope"]:  # this requires transformation into world coords after inference
            if img is not None:
                if self.src == "yolact":
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) #fix colors
                    mask, centroid = self.get_obj_pixel_position(obj, img)
                    # cv2.imshow("Mask", mask)
                    # cv2.imshow("Depth", depth)
                    # cv2.imshow("Inference input", img)
                    # cv2.waitKey(1)
                    centroid_transformed = self.yolact_cnn.find_3d_centroids_(mask, depth, self.env.unwrapped.cameras[self.env.active_cameras].view_x_proj)
                    if centroid_transformed.size == 3:
                        self.centroid_transformed[obj.get_name()] = centroid_transformed
                        #print("{} was detected at {}".format(obj.get_name(),self.centroid_transformed[obj.get_name()]))
                    elif obj.get_name() not in self.centroid_transformed.keys():
                        self.centroid_transformed[obj.get_name()] = [10, 10, 10]
                        #print("{} was not detected, assign {}".format(obj.get_name(),self.centroid_transformed[obj.get_name()]))
                    else:
                        pass
                        #print("{} was not detected, assign previous {}".format(obj.get_name(),self.centroid_transformed[obj.get_name()]))
                    return list(self.centroid_transformed[obj.get_name()])
                    #return list(centroid)
            else:
                raise Exception("You need to provide image argument to infer object position")
        return

    def get_obj_orientation(self, obj=None, img=None):
        """Returns object orientation inferred from image (img argument) or retrieved from obj (obj argument)"""
        # @TODO
        if self.src == "ground_truth":
            if obj is not None:
                return obj.get_orientation()
            else:
                raise Exception("You need to provide obj argument to get gt orientation")
        elif self.src in ["yolact", "dope"]:
            if img is not None:
                pass
            else:
                raise Exception("You need to provide image argument to infer orientation")
        return

    def encode_with_vae(self, img):
        """Encodes the input image into an n-dimensional latent variable using a pre-trained variational autoencoder
        !!Currently only supports input square images """
        if self.src != "vae":
            raise Exception("Encoding can only be done with VAE module!")
        else:
            img = cv2.resize(img, (128,128))
            img = torch.tensor(img).type(torch.FloatTensor)
            img = img.reshape(img.shape[2], img.shape[0], img.shape[0]).unsqueeze(0)
            latent_z = self.vae_embedder.infer(img.cpu())[0].detach().cpu()
        return latent_z

    def inference_yolact(self, img):
        classes, class_names, scores, boxes, masks, centroids = self.yolact_cnn.raw_inference(img)
        return classes, class_names, scores, boxes, masks, centroids

    def _initialize_network(self, network):
        # @TODO
        if network == "vae":
            weights_pth = pkg_resources.resource_filename("ciircgym", '/trained_models/vae_img128_64dim/model_best.pth.tar')
            self.vae_embedder = load_checkpoint(weights_pth, use_cuda=True)
            self.obsdim = 2*self.vae_embedder.n_latents
        elif network == "yolact":
            #path to weights
            weights = pkg_resources.resource_filename("ciircgym", 'yolact_vision/data/yolact/weights/weights_yolact_ciircgym_23/crow_base_15_266666.pth')
            #path to saved config obj or name of an existing one in the Config script (e.g. 'yolact_base_config') or None for autodetection
            config = pkg_resources.resource_filename("ciircgym", 'yolact_vision/data/yolact/weights/weights_yolact_ciircgym_23/config_train_15.obj')
            self.yolact_cnn = InfTool(weights=weights, config=config, score_threshold=0.2)
            self.obsdim = 6
        elif network == "dope":
            self.obsdim = 14
        return

