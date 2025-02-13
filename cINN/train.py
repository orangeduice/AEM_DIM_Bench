"""
This file serves as a training interface for training the network
"""
# Built in
import glob
import os
import shutil
import sys
sys.path.append('/home/yw/Documents/oscar_work/AEM_DIM_Bench/')
# Torch
import torch
# Own
import flag_reader
from utils import data_reader
from class_wrapper import Network
from model_maker import cINN
from utils.helper_functions import put_param_into_folder,write_flags_and_BVE
from evaluate import evaluate_from_model
import numpy as np

def training_from_flag(flags):
    """
    Training interface. 1. Read data 2. initialize network 3. train network 4. record flags
    :param flag: The training flags read from command line or parameter.py
    :return: None
    """
    # Get the data
    train_loader, test_loader = data_reader.read_data(flags)
    print("Making network now")

    # Make Network
    ntwk = Network(cINN, flags, train_loader, test_loader)

    print("number of trainable parameters is :")
    pytorch_total_params = sum(p.numel() for p in ntwk.model.parameters() if p.requires_grad)
    print(pytorch_total_params)

    # Training process
    print("Start training now...")
    ntwk.train()

    # Do the house keeping, write the parameters and put into folder, also use pickle to save the flags obejct
    write_flags_and_BVE(flags, ntwk.best_validation_loss, ntwk.ckpt_dir)


def retrain_different_dataset(index):
    """
    This function is to evaluate all different datasets in the model with one function call
    """
    from utils.helper_functions import load_flags
    #data_set_list = ["Peurifoy"]
    # data_set_list = ["Chen"]
    # data_set_list = ["Yang"]
    data_set_list = ["Peurifoy","Chen","Yang"]
    for eval_model in data_set_list:
        flags = load_flags(os.path.join("models", eval_model+"_best_model"))
        flags.data_dir = '~/Documents/oscar_work/AEM_DIM_Bench/Data/'
        flags.model_name = "retrain" + str(index) + eval_model
        flags.train_step = 500
        flags.test_ratio = 0.2
        training_from_flag(flags)

def hyperswipe():
    """
    This is for doing hyperswiping for the model parameters
    """
    reg_scale_list = [1e-4]
    lr_list = [1e-3, 1e-2]
    # lr_list = [1e-1, 1e-2, 1e-3, 1e-4]
    #reg_scale_list = [1e-2, 1e-3, 1e-1]
    for reg_scale in reg_scale_list:
        for couple_layer_num in [14, 16, 18]:#range(12,):    
            for lr in lr_list:
                for i in range(1, 3):
                    flags = flag_reader.read_flag()  	#setting the base case
                    flags.couple_layer_num = couple_layer_num
                    flags.lr = lr
                    flags.reg_scale = reg_scale
                    flags.model_name = flags.data_set + '_mid_layer_1024_couple_layer_num' + str(couple_layer_num) +  '_lr_' + str(flags.lr) + '_reg_scale_' + str(reg_scale) + '_trail_' + str(i)
                    training_from_flag(flags)


def random_swipe():
    """
    This is the random version of hyperswiping for the model parameters
    """
    # The list of params that signified by a lower and upper limit and use np.random.uniform to select
    lambda_mse_range = [1, 1000]
    lambda_z_range = [1, 1000]
    lambda_rev_range = [1, 1000]
    # The list of params that signified by a permutation of the values in the list
    zeros_noise_scale_list = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
    y_noise_scale_list = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    # Number of samples to draw
    num_samples = 60
    for i in range(num_samples):
        flags = flag_reader.read_flag()  	#setting the base case
        flags.lambda_mse = np.random.uniform(low=lambda_mse_range[0], high=lambda_mse_range[1])
        flags.lambda_z = np.random.uniform(low=lambda_z_range[0], high=lambda_z_range[1])
        flags.lambda_rev = np.random.uniform(low=lambda_rev_range[0], high=lambda_rev_range[1])
        flags.zeros_noise_scale = zeros_noise_scale_list[np.random.permutation(len(zeros_noise_scale_list))[0]]
        flags.y_noise_scale = y_noise_scale_list[np.random.permutation(len(y_noise_scale_list))[0]]
        flags.model_name = flags.data_set + 'lambda__mse_{:.2g}_z_{:.2g}_rev_{:.2g}_noise__zeros_{:.3g}_y_{:.3g}'.format(flags.lambda_mse,
                        flags.lambda_z, flags.lambda_rev, flags.zeros_noise_scale, flags.y_noise_scale)
        training_from_flag(flags)


if __name__ == '__main__':
    # Read the parameters to be set
    #flags = flag_reader.read_flag()
    
    #random_swipe()
    # hyperswipe()
    
    # Call the train from flag function
    #training_from_flag(flags)
    
    #retrain_different_dataset(0)

    # Do the retraining for all the data set to get the training for reproducibility
    for i in range(0,10):
       retrain_different_dataset(i)
