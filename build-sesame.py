#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def main():
    build_for = os.getenv('SESAME_BUILD_FOR', '')
    if build_for == 'android':
        from sesame import build_template_default
        builder = build_template_default.get_builder()
        builder.run()
    else:
        from bincrafters import build_template_default
        builder = build_template_default.get_builder()
        builder.run()

if __name__ == '__main__':
    main()
