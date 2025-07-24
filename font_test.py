#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Font encoding test script
"""
import pygame
import sys

def test_fonts():
    pygame.font.init()
    
    # Test Japanese text
    test_text = "報酬を選択"
    
    print("Testing font rendering capabilities...")
    print(f"Test text: {test_text}")
    print(f"Text encoding: {test_text.encode('utf-8')}")
    
    # Test default font
    try:
        default_font = pygame.font.Font(None, 24)
        surface = default_font.render(test_text, True, (255, 255, 255))
        print("✓ Default font can render Japanese text")
        print(f"Surface size: {surface.get_size()}")
    except Exception as e:
        print(f"✗ Default font cannot render Japanese text: {e}")
    
    # Test MS Gothic font
    try:
        msgothic_font = pygame.font.SysFont('msgothic', 24)
        surface = msgothic_font.render(test_text, True, (255, 255, 255))
        print("✓ MS Gothic font can render Japanese text")
        print(f"Surface size: {surface.get_size()}")
    except Exception as e:
        print(f"✗ MS Gothic font cannot render Japanese text: {e}")
    
    # List available fonts containing 'gothic'
    fonts = pygame.font.get_fonts()
    gothic_fonts = [f for f in fonts if 'gothic' in f]
    print(f"\nAvailable Gothic fonts: {gothic_fonts}")

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"System encoding: {sys.getdefaultencoding()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    test_fonts()