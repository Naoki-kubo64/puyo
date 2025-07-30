#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame
import sys

def test_fonts():
    pygame.font.init()
    
    # Test Japanese text
    test_text = "報酬を選択"
    
    print("Testing font rendering...")
    
    # Test default font
    try:
        default_font = pygame.font.Font(None, 24)
        surface = default_font.render(test_text, True, (255, 255, 255))
        print("Default font OK - Size:", surface.get_size())
    except Exception as e:
        print("Default font FAIL:", str(e))
    
    # Test MS Gothic font
    try:
        msgothic_font = pygame.font.SysFont('msgothic', 24)
        surface = msgothic_font.render(test_text, True, (255, 255, 255))
        print("MS Gothic font OK - Size:", surface.get_size())
    except Exception as e:
        print("MS Gothic font FAIL:", str(e))

if __name__ == "__main__":
    test_fonts()