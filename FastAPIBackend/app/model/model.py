from torchvision import transforms
import torch
from PIL import Image
from  torchvision.models import resnet18 
from typing import List, Dict
from fastapi import FastAPI, File, UploadFile
import os


class ResNet18:
    def __init__(self) -> None:
        self.resnet = resnet18(weights='DEFAULT')
        self.resnet.eval()
        self.transform  = transforms.Compose([transforms.Resize(256),                    
                                            transforms.CenterCrop(224),                
                                            transforms.ToTensor(),                     
                                            transforms.Normalize(                      
                                            mean=[0.485, 0.456, 0.406],                
                                            std=[0.229, 0.224, 0.225]                  
                                            )])
    

    def __predict(self, batched_img) -> List[Dict]:
        with torch.no_grad():
            output = self.resnet(batched_img)
            probs = torch.nn.functional.softmax(output, dim=1)
            topk_indices = torch.topk(probs, k=10).indices

        # Print the predicted class label
        topk_indices = topk_indices.tolist() 
        topk_indices_probs  = []
        for idx, instance  in enumerate(topk_indices): 
            topk_indices_probs.append({i:probs[idx, i].item() for i in instance})

        return topk_indices_probs 

    def __idx2label(self, topk_indices_probs: List[Dict]) -> List[Dict]:
        current_file_dir = os.path.dirname(os.path.abspath(__file__))

        with open(current_file_dir+'/imagenet_classes.txt', 'r') as f:
            class_names = [line.strip() for line in f.readlines()]
            
        predicted_names_prob = []
        for instance in topk_indices_probs:
            name_prob = [(class_names[k], float(v)) for k,v  in instance.items()]
            predicted_names_prob.append(name_prob)

        return predicted_names_prob

    def predict_pipeline(self, imgs) -> List[Dict]:
        pred_idx = self.__predict(imgs)
        pred_label = self.__idx2label(pred_idx)


        return  pred_label
    

