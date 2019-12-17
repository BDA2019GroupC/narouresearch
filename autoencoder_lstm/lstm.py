# -*- coding: utf-8 -*-
"""lstm.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17BOHCg3aQNhkvMdVJJ19-hXV2T1MIHPc
"""

import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

import sys

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.manual_seed(1)
random_state = 0

BOS = 0
EOS = 1
UNK = 2

class Encoder(nn.Module):
  def __init__(self, input_size, embedding_size, hidden_size):
    # input_size: 入力のuniqueな単語数
    # hidden_size: 隠れ層のユニット数
    super(Encoder, self).__init__()
    self.embedding_size = embedding_size
    self.input_size     = input_size
    self.hidden_size    = hidden_size
    self.embedding      = nn.Embedding(input_size, embedding_size) # paddingなし
    self.LSTM           = nn.LSTM(embedding_size, hidden_size, num_layers=1) # input_sizeはともかく隠れ層のユニット数hiddenでいいのか？

  def forward(self, batch, hidden=None):
    embedding = self.embedding(batch) # 文字のベクトル表現を取ってくる？
    _, hidden = self.LSTM(embedding, hidden)
    return hidden

class Decoder(nn.Module):
  def __init__(self, embedding_size, hidden_size, output_size):
    #vocab_size: 出力のuniqueな単語数
    super(Decoder, self).__init__()
    self.embedding_size = embedding_size
    self.hidden_size    = hidden_size
    self.output_size    = output_size
    self.embedding      = nn.Embedding(output_size, embedding_size)
    self.LSTM           = nn.LSTM(embedding_size, hidden_size, num_layers=1)
    self.out            = nn.Linear(hidden_size, output_size)

  def forward(self, batch, hidden):
    embedding = self.embedding(batch)
    output, hidden = self.LSTM(embedding, hidden)
    output = self.out(output)
    return output, hidden

class EncoderDecoder(nn.Module):
  def __init__(self, input_size, embedding_size, hidden_size, output_size, teacher_forcing_rate=0.5):
    super(EncoderDecoder, self).__init__()
    self.teacher_forcing_rate = teacher_forcing_rate
    self.input_size     = input_size
    self.embedding_size = embedding_size
    self.hidden_size    = hidden_size
    self.output_size    = output_size
    self.encoder = Encoder(input_size, embedding_size, hidden_size)
    self.decoder = Decoder(embedding_size, hidden_size, output_size)

  def forward(self, seq): # seqは１文章ずつ seq = tensor([BOS, chr_id1, chr_id2, ... , EOS])
    encoder_hidden = None
    seq_len = len(seq)
    for chr_id in seq:
      encoder_input = chr_id.view(1,1)
      encoder_hidden = self.encoder(encoder_input, encoder_hidden)
    decoder_outputs = torch.zeros(seq_len-1, 1, self.output_size, device=device) # BOSは生成しない 入力が1文章なので、第二引数は1
    decoder_input = seq[0].view(1,1) # = BOS
    decoder_hidden = encoder_hidden
    for i in range(seq_len-1):
      decoder_output, decoder_hidden = self.decoder(decoder_input, decoder_hidden)
      decoder_outputs[i] = decoder_output
      # teacher-forcing
      teacher_forcing = (random.random() < self.teacher_forcing_rate)
      decoder_input = seq[i+1].view(1,1) if (teacher_forcing) else decoder_output.argmax().view(1,1) 
    return decoder_outputs

  def gen(self, seq, max_length=-1): # 文章生成するときってteacher_forcingなしかなと思って追加した seq = tensor([BOS, chr_id1, chr_id2, ... , EOS])
    encoder_hidden = None
    if(max_length <= 0): max_length = len(seq) - 2
    for chr_id in seq:
      encoder_input = chr_id.view(1,1)
      encoder_hidden = self.encoder(encoder_input, encoder_hidden)
    generated_seq = []
    decoder_input = seq[0].view(1,1) # = BOS
    decoder_hidden = encoder_hidden
    for i in range(max_length):
      decoder_output, decoder_hidden = self.decoder(decoder_input, decoder_hidden)
      decoder_input = decoder_output.argmax().view(1,1)
      generated_id = int(decoder_input)
      if(generated_id < 32): break
      generated_seq.append(generated_id)
    return torch.tensor(generated_seq, device=device)