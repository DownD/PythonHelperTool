import logging
from argparse import ArgumentParser, Namespace
from typing import Optional

import cv2
import numpy as np
import onnxruntime as ort

from myutils.script_interface import ScriptInterface

LOGGER = logging.getLogger(__name__)


# pylint: disable=attribute-defined-outside-init
class CVInference(ScriptInterface):
    """
    This class runs inference using YOLO on a video or window.
    """

    def __init__(self):
        super().__init__(
            "cv_inference",
            """Runs inference using ONNX runtime on a video or window.
            Either a -v or -wnd needs to be provided.
            """,
        )

    def init(
        self,
        weights_path: str,
        class_names: Optional[list[str]] = None,
        model_format: str = "yolo",
        conf_tresh: float = 0.7,
        iou_tresh: float = 0.5,
        input_shape: Optional[tuple[int, int]] = None,
        use_gpu=True,
    ):
        """
        Initializes the inference engine.
        """
        self.weights_path = weights_path
        self.format = model_format
        self.conf_tresh = conf_tresh
        self.iou_tresh = iou_tresh
        self.colors_array: dict[int, tuple[int, int, int]] = {}

        if class_names:
            self.class_names = class_names
        else:
            self.class_names = []

        self.providers = []

        if use_gpu:
            self.providers.append("CUDAExecutionProvider")
        else:
            self.providers.append("CPUExecutionProvider")

        self.session = ort.InferenceSession(
            self.weights_path, providers=self.providers
        )
        self.outname = [i.name for i in self.session.get_outputs()]
        self.inname = [i.name for i in self.session.get_inputs()]

        if input_shape is None:
            # Get input shape from the model
            model_input_shape = self.session.get_inputs()[0].shape
            self.input_shape = (model_input_shape[2], model_input_shape[3])
        else:
            self.input_shape = input_shape

    def get_color(self, class_id: int) -> tuple[int, int, int]:
        """
        Generates a random color for each class id and caches it.

        Args:
            class_id (int): The class id

        Returns:
            tuple[int, int, int]: The color
        """

        # Cache colors
        if class_id not in self.colors_array:
            self.colors_array[class_id] = tuple(  # type: ignore
                np.random.randint(0, 255, size=3).tolist()
            )

        return self.colors_array[class_id]

    def letterbox(
        self,
        im: np.ndarray,
        new_shape=(640, 640),
        color=(114, 114, 114),
        auto=True,
        scaleup=True,
        stride=32,
    ) -> tuple[np.ndarray, float, tuple[float, float]]:
        """
        Resize a rectangular image to a padded rectangular.

        Args:
            im (ndarray): _description_
            new_shape (tuple, optional): New shape to be resized to. Defaults to (1280, 1280).
            color (tuple, optional): Color of the border. Defaults to (114, 114, 114).
            auto (bool, optional): _description_. Defaults to True.
            scaleup (bool, optional): _description_. Defaults to True.
            stride (int, optional): _description_. Defaults to 32.

        Returns:
            tuple[np.ndarray, float, tuple[float, float]]: _description_
        """

        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if (
            not scaleup
        ):  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = (
            new_shape[1] - new_unpad[0],
            new_shape[0] - new_unpad[1],
        )

        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

        dw /= 2
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(
            im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
        )
        return im, r, (dw, dh)

    def run_inference(
        self, img, resize: bool = True
    ) -> list[tuple[int, float, float, float, float, int, float]]:
        """
        Runs inference on the image.
        The output is expressed in absolute coordinates of the image size.

        Yolo format:
            Input: (batch_size, color_channels, height, width)
            Output: (natch_id, x0, y0, x1, y1, class_id, confidence)
        Args:
            img (ndarray): Image to run inference on.

        Returns:
            list[tuple[int batch_id, float x0, float y0, float x1, float y1, int class_id, float score]]
        """

        if self.format == "yolo":
            img_tmp = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if resize:
                img_tmp, r, dwdh = self.letterbox(
                    img_tmp, new_shape=self.input_shape, auto=False
                )
            img_tmp = img_tmp.astype("float32")

            # Yolo requires the image to be in the format (C, H, W)
            img_tmp = img_tmp.transpose((2, 0, 1))

            # Yolo requires the image to be in the format (N, C, H, W)
            img_tmp = np.expand_dims(img_tmp, 0)

            # Yolo requires the image to be contiguous
            img_tmp = np.ascontiguousarray(img_tmp)

            # Normalize the bytes of the image
            img_tmp = img_tmp / 255.0

            out = self.session.run(self.outname, {self.inname[0]: img_tmp})

            # Match the box coordinates to the resized image
            if resize:
                out[0][:, 1:5] = (out[0][:, 1:5] - np.array(dwdh * 2)) / r
            return out[0]

        raise ValueError(f"Unknown format {self.format}")

    def draw_run_inference(self, img: np.ndarray):
        """
        This function runs and draws the inference boxes on the image.

        Args:
            img (np.ndarray): Image to run inference on.
        """

        vals = self.run_inference(img)
        for batch_id, x0, y0, x1, y1, cls_id, score in vals:
            box = np.array([x0, y0, x1, y1])
            box = box.round().astype(np.int32).tolist()
            cls_int_id = int(cls_id)
            color = self.get_color(cls_int_id)
            if len(self.class_names) > cls_int_id:
                label = f"{self.class_names[cls_int_id]} {score:.2f}"
            else:
                label = f"{cls_int_id} {score:.2f}"
            cv2.rectangle(img, box[:2], box[2:], color, 2)
            cv2.putText(
                img,
                label,
                (box[0], box[1] - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                [225, 255, 255],
                thickness=2,
            )

    def run_video(self, video_file: str):
        """
        Runs inference on a video file

        Args:
            video_file (str): Path to the video file
        """
        cv2.namedWindow("Inference Window", cv2.WINDOW_NORMAL)
        cap = cv2.VideoCapture(video_file)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            self.draw_run_inference(frame)
            cv2.imshow("Inference Window", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def add_subparser_args(self, parser: ArgumentParser):
        """
        This function ads arguments for the script.

        Args:
            parser (ArgumentParser): The subparser of the script
        """
        parser.add_argument(
            "-v",
            "--video_file",
            type=str,
            default=None,
            const=None,
            nargs="?",
            help="Path to the video file, cannot be combined with --window",
            required=False,
        )
        parser.add_argument(
            "model_weights_path",
            type=str,
            help="The path to the weights of the model",
        )
        parser.add_argument(
            "-f",
            "--model_format",
            default="yolo",
            const="yolo",
            type=str,
            choices=["yolo"],
            nargs="?",
            help="The path to the YOLO model",
        )
        parser.add_argument(
            "-wnd",
            "--window_name",
            type=str,
            default=None,
            const=None,
            nargs="?",
            help="Name of the window to run inference on, cannot be combined with option --video_file. CURRENTLY NOT IMPLEMENTED",
            required=False,
        )

        parser.add_argument(
            "-c",
            "--conf_tresh",
            type=float,
            default=None,
            const=None,
            nargs="?",
            help="The confidence threshold for the model",
            required=False,
        )

        parser.add_argument(
            "-i",
            "--iou_tresh",
            type=float,
            default=None,
            const=None,
            nargs="?",
            help="The IoU threshold for the model",
        )

        parser.add_argument(
            "--cpu", help="Do not use GPU", action="store_true"
        )

        parser.add_argument(
            "-nc",
            "--nc_path",
            type=str,
            default=None,
            const=None,
            nargs="?",
            help="Path to the class names file",
            required=False,
        )

    def __call__(self, args: Namespace):
        """
        This is the main function of the cpp_tools script.

        Args:
            args (Namespace): _description_
        """

        if args.video_file is not None and args.window_name is not None:
            raise ValueError(
                "Cannot use both --video_file and --window_name at the same time"
            )

        if args.video_file is None and args.window_name is None:
            raise ValueError(
                "Must use either --video_file or --window_name at the same time"
            )

        model_path = args.model_weights_path

        kwargs = {}
        if args.conf_tresh:
            kwargs["conf_tresh"] = args.conf_tresh

        if args.iou_tresh:
            kwargs["iou_tresh"] = args.iou_tresh

        kwargs["use_gpu"] = not args.cpu

        if args.nc_path:
            with open(args.nc_path, "r", encoding="utf-8") as file:
                nc = file.read().splitlines()
                kwargs["class_names"] = nc

        kwargs["model_format"] = args.model_format

        self.init(model_path, **kwargs)

        if args.video_file:
            self.run_video(args.video_file)

        if args.window_name:
            raise NotImplementedError("Not implemented yet")
