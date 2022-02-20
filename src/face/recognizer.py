import numpy as np
import cv2
import os
import tkinter as tk
from face.preprocess import preprocessing, path_prefix
from pathlib import Path
from PIL import Image, ImageTk


authorize_text = ''
dialog_text = ''
current_face=None


def set_authorize_text(s):
    global authorize_text
    authorize_text = s


def set_dialog_text(s):
    global dialog_text
    dialog_text = s

class Recogniser:
    def __init__(self):
        self.face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()

    def get_faces(self, img):
        """ Extracting all faces from image"""

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces

    def recognize_faces(self, faces, img, config, sampling=None):
        """ Trying to recognize every face from image"""
        global current_face
        accuracy_for_authorize = 55
        font = cv2.FONT_HERSHEY_DUPLEX
        current_face = None
        for (x1, y1, x2, y2) in faces:
            try:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cropped_gray = gray[y1:y1 + y2, x1:x1 + x2]
                id, confidence = self.face_recognizer.predict(cropped_gray)
                if confidence < 100 - accuracy_for_authorize:
                    id = config.user_dict_reverse[str(id)][0]
                    confidence = "  {0}%".format(round(100 - confidence))
                    color = (0, 255, 0)
                    set_authorize_text('Authorized!\nUser: {}'.format(id))
                    current_face = id
                else:
                    id = 'unknown'
                    confidence = ''
                    color = (0, 0, 255)
                    set_authorize_text('Not authorized :(\n Unknown user')
            except:
                id = ''
                confidence = ''
                color = (255, 255, 255)
                set_authorize_text('no recognizer trained yet')
            if sampling:
                color = (0, 255, 255)
            if dialog_text != 'Already created' and dialog_text != 'Invalid username':
                set_dialog_text('detecting user face')
            cv2.putText(img, str(id), (x1 + 5, y1 - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x1 + 5, y1 + y2 - 5), font, 1, (255, 255, 0), 1)
            cv2.rectangle(img, (x1, y1), (x1 + x2, y1 + y2), color, 2)

        if len(faces) == 0:
            set_authorize_text('No user')
            set_dialog_text('cant see any face')

    def update(self):
        """ Read recognizer from file"""

        try:
            self.face_recognizer.read(path_prefix+'faces.yml')
        except:
            pass

    def train(self, config):
        """ Train and save recognizer """

        train_set = self.prepare_train_set(config.save_path_gray, config.user_dict)
        self.face_recognizer.train(*train_set)
        self.face_recognizer.write(path_prefix+'faces.yml')

    @staticmethod
    def prepare_train_set(save_path_gray, user_dict):
        """ Prepare training set from users directories for recogniser to train"""

        faces = []
        ids = []
        for directory in os.listdir(save_path_gray):
            for file in os.listdir(save_path_gray + directory + '/'):
                image = np.array(Image.open(save_path_gray + directory + '/' + file))
                faces.append(image)
                ids.append(int(user_dict[directory]))
        return faces, np.array(ids)


class Configure():

    def __init__(self, options):
        self.save_path_color = options[0]
        self.save_path_gray = options[1]

    def update_user_dict(self):
        """ Read users.txt """

        user_dict = {}
        user_dict_reverse = {}
        with open(path_prefix+'users.txt', 'r') as f:
            lines = f.readlines()
            user_count = len(lines)
            for entry in lines:
                splitted = entry.split()
                user = splitted[0]
                id = splitted[1]
                user_dict[user.split(':')[1]] = id.split(':')[1]
                user_dict_reverse[str(id.split(':')[1])] = [user.split(':')[1]]
        self.user_count = user_count
        self.user_dict = user_dict
        self.user_dict_reverse = user_dict_reverse


class User():

    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.sample_id = 1

    def to_user_list(self, config):
        """ Create user dir and write username,id to users.txt"""

        path = config.save_path_gray
        path += '{}/'.format(self.name)
        if Path(path).is_dir():
            print('Already created')
            return False
        else:
            os.mkdir(path)
            with open(path_prefix+'users.txt', 'a') as f:
                f.write('User:{} Id:{}'.format(self.name, config.user_count) + '\n')
            config.update_user_dict()

    def samples(self):
        return self.samples

    def make_sample(self, recognizer, config):
        """ Making users 'photos' """

        path = config.save_path_gray
        ret, img = cap.read()
        faces = recognizer.get_faces(img)
        if len(faces) == 0:
            set_dialog_text('can\'t see ur face')
            return False
        else:
            for (x1, y1, x2, y2) in faces:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cropped_gray = gray[y1:y1 + y2, x1:x1 + x2]
                self.write_user_sample(cropped_gray, self.sample_id, path)
                self.sample_id += 1
                set_dialog_text('Sampling, {}/160'.format(self.sample_id))
            if 50 <= self.sample_id <= 65:
                set_dialog_text('smile plz')
            if 100 <= self.sample_id <= 115:
                set_dialog_text('move your face in a circle')
            if self.sample_id >= 160:
                set_dialog_text('Sampled, started training..')
                recognizer.train(config)
                recognizer.update()
                set_dialog_text('Sampled and trained')
                return True
            return False

    def write_user_sample(self, image, sample_id, path):
        cv2.imwrite(path + '{}/'.format(self.name) + 'sample_{}.png'.format(sample_id), image)


class VideoThread:

    def __init__(self, recognizer, config):
        self.recognizer = recognizer
        self.config = config
        self.sampling = False

    def start_sampling(self, username):
        """ If button pressed, start sampling"""
        if username not in self.config.user_dict and not self.sampling:
            new_user = User(username, self.config.user_count)
            self.waiting_user = new_user
            self.sampling = True
            new_user.to_user_list(self.config)
        else:
            set_dialog_text('Already created')


    def highlight_faces(self, img, sampling):
        """ Draw rectangles """

        faces = self.recognizer.get_faces(img)
        recognizer.recognize_faces(faces, img, self.config, sampling)

    def show_pic(self):
        ret, frame = cap.read()
        self.highlight_faces(frame, self.sampling)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = frame

        preview_image = Image.fromarray(rgb)
        if self.sampling:
            sampled = self.waiting_user.make_sample(self.recognizer, self.config)
            if sampled:
                self.sampling = False

        cv2.putText(rgb, dialog_text, (20, 20), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
        _, imgres = cv2.imencode('.jpg', rgb)

        return imgres.tostring()
        # image_label.tk_image = tk_image
        # image_label.configure(image=tk_image)
        # image_label.after(5, self.show_pic)


def get_current_face():
    return current_face

def end():
    # root.destroy()
    cap.release()
    cv2.destroyAllWindows()


def create_vt():
    global cap, config, recognizer

    # TODO: change cam id
    cap = cv2.VideoCapture(0)
    config = Configure(preprocessing())
    config.update_user_dict()
    recognizer = Recogniser()
    recognizer.update()
    return VideoThread(recognizer, config)


