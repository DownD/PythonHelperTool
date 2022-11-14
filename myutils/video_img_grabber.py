import logging
import os
from argparse import ArgumentParser, Namespace

import cv2

from myutils.script_interface import ScriptInterface

LOGGER = logging.getLogger(__name__)


class VideoImgSplit(ScriptInterface):
    """
    This class grabs images from a video file and saves them to a folder.
    """

    def __init__(self):
        super().__init__(
            "video_img_split", "This script grabs images from a video file"
        )

    def add_subparser_args(self, parser: ArgumentParser):
        """
        This function ads arguments for the script.

        Args:
            parser (ArgumentParser): The subparser of the script
        """
        parser.add_argument(
            "video_file",
            type=str,
            help="Path to the video file",
        )
        parser.add_argument(
            "-s",
            "--save_images_path",
            type=str,
            const="",
            default="",
            nargs="?",
            help="The path where the images will be saved",
        )
        parser.add_argument(
            "-d",
            "--delay",
            type=float,
            const=5.0,
            default=5.0,
            nargs="?",
            help="The delay between frames in seconds",
        )

    def __call__(self, args: Namespace):
        """
        This is the main function of the cpp_tools script.

        Args:
            args (Namespace): _description_
        """

        # Check if img paths exists
        img_path = args.save_images_path
        if not os.path.isdir(img_path) and img_path != "":
            LOGGER.info("Creating directory %s", img_path)
            os.makedirs(img_path)

        # Open video file
        video = cv2.VideoCapture(args.video_file)
        if not video.isOpened():
            LOGGER.error("Error opening video file %s", args.video_file)
            return

        # Loop trough video by delay
        curr_time = args.delay
        counter = 0
        while video.isOpened():
            video.set(cv2.CAP_PROP_POS_MSEC, curr_time * 1000)
            success, img = video.read()
            if not success:
                break
            img_name = f"{int(curr_time*1000)}.jpg"
            img_path = os.path.join(args.save_images_path, img_name)
            cv2.imwrite(img_path, img)
            curr_time += args.delay
            counter += 1
            LOGGER.debug("Saved image %s", img_path)

        LOGGER.info("Saved %d images", counter)
