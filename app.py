# visitorLogger - A simple visitor logger for the website
# https://github.com/lwd-temp/visitorLogger
# Flask Backend
import sqlite3
import time

import flask

#######CONFIGURATION########
# Default Secret Key
SECRET_KEY = 'developmentkey'
# Default Database Name
DATABASE = 'visitor.db'
# Default Port
PORT = 80
# Default Host
HOST = '0.0.0.0'
# Debug Mode
DEBUG = False
# Default API URL in JavaScript
API_URL = 'http://example.com/append'
# JS Path
JS = "visitorLogger.js"
# GzipBomb Anti-Attack
GZIP_BOMB = False
#######CONFIGURATION########


# Return GzipBomb when permission denied
def permission_denied():
    if GZIP_BOMB:
        return GzipBombResponse(size='10G')
    else:
        return flask.Response(
            "Permission Denied",
            mimetype="text/plain",
            status=403
        )


# GzipBomb Protection
# https://github.com/kuszaj/Flask-GzipBomb
# Raw gzipped data used in GzipBombResponse.
rawdata = {
    '1k': bytearray((
        0x1f, 0x8b, 0x08, 0x00, 0xca, 0x77, 0x62, 0x59,
        0x02, 0x03, 0x63, 0x60, 0x18, 0x05, 0xa3, 0x60,
        0x14, 0x8c, 0x54, 0x00, 0x00, 0x2e, 0xaf, 0xb5,
        0xef, 0x00, 0x04, 0x00, 0x00
    )),
    '10k': bytearray((
        0x1f, 0x8b, 0x08, 0x00, 0xcb, 0x77, 0x62, 0x59,
        0x02, 0x03, 0xed, 0xc1, 0x01, 0x0d, 0x00, 0x00,
        0x00, 0xc2, 0xa0, 0xf7, 0x4f, 0x6d, 0x0e, 0x37,
        0xa0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x80, 0x37, 0x03, 0x9a, 0xde, 0x1d,
        0x27, 0x00, 0x28, 0x00, 0x00
    )),
    '100k': bytearray((
        0x1f, 0x8b, 0x08, 0x00, 0xcb, 0x77, 0x62, 0x59,
        0x02, 0x03, 0x93, 0xef, 0xe6, 0x60, 0x38, 0x5d,
        0x9e, 0x14, 0xc9, 0xc4, 0xfc, 0xf6, 0x20, 0x23,
        0x23, 0x03, 0x03, 0x43, 0x93, 0xc2, 0xff, 0xf5,
        0x79, 0x1e, 0x0e, 0x20, 0x26, 0x8d, 0x41, 0x8d,
        0x44, 0x62, 0xeb, 0x0f, 0x2f, 0x86, 0x09, 0x8c,
        0x0c, 0x00, 0x62, 0x5b, 0xc0, 0x8c, 0x85, 0x00,
        0x00, 0x00
    )),
    '1M': bytearray((
        0x1f, 0x8b, 0x08, 0x00, 0xca, 0x77, 0x62, 0x59,
        0x02, 0x03, 0x93, 0xef, 0xe6, 0x60, 0x38, 0x55,
        0x9e, 0x14, 0xc9, 0xc4, 0xfc, 0xf6, 0xa0, 0x21,
        0x23, 0x03, 0x03, 0xc3, 0xa1, 0x05, 0x5f, 0xfd,
        0x73, 0x39, 0xe2, 0x17, 0x30, 0x8c, 0x82, 0x51,
        0x30, 0x0a, 0x46, 0x1c, 0xb0, 0x63, 0x96, 0x79,
        0x65, 0xb1, 0x9c, 0x81, 0x41, 0x80, 0x01, 0x00,
        0xa8, 0x32, 0x11, 0xcf, 0x1b, 0x04, 0x00, 0x00
    )),
    '10M': bytearray((
        0x1f, 0x8b, 0x08, 0x00, 0xca, 0x77, 0x62, 0x59,
        0x02, 0x03, 0xed, 0xd0, 0xb1, 0x0d, 0x82, 0x50,
        0x14, 0x40, 0xd1, 0xc7, 0xa7, 0x01, 0x97, 0xa0,
        0x67, 0x05, 0x2b, 0xe2, 0x14, 0x54, 0x26, 0x2e,
        0x41, 0x4b, 0x62, 0x69, 0xe3, 0x04, 0xc6, 0x0d,
        0x98, 0xc1, 0xd8, 0x11, 0x37, 0x70, 0x05, 0x43,
        0x98, 0x00, 0x0c, 0x63, 0x90, 0x9c, 0x53, 0xdd,
        0xfa, 0x56, 0xb7, 0x22, 0xc6, 0xee, 0xd2, 0xa6,
        0xfc, 0xf7, 0xca, 0xb2, 0x88, 0xe8, 0xef, 0xcb,
        0x30, 0x15, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x76, 0xae, 0xff, 0x5e, 0x4f,
        0x69, 0x8b, 0x66, 0x3d, 0x1f, 0xdf, 0xc9, 0x10,
        0x00, 0xd8, 0x81, 0xb9, 0xfc, 0xd4, 0xe3, 0x23,
        0xe2, 0x19, 0x7f, 0x31, 0xd9, 0x23, 0x9c, 0xe0,
        0x27, 0x00, 0x00
    )),
    '100M': bytearray((
        0x1f, 0x8b, 0x08, 0x00, 0xca, 0x77, 0x62, 0x59,
        0x02, 0x03, 0x93, 0xef, 0xe6, 0x60, 0x38, 0x55,
        0x9e, 0x14, 0xc9, 0xc4, 0xfc, 0xf6, 0xee, 0x7a,
        0x3f, 0xa7, 0x44, 0x99, 0xe3, 0x0f, 0x8b, 0x6d,
        0xd2, 0xfb, 0x24, 0x7f, 0x08, 0x7b, 0xb0, 0xdc,
        0xd4, 0x89, 0x63, 0x6a, 0xe5, 0xe5, 0x3a, 0xea,
        0x74, 0x20, 0x61, 0x62, 0xa2, 0xba, 0xb4, 0xa5,
        0xb4, 0x72, 0xa4, 0x4e, 0xde, 0xbd, 0xd6, 0x4e,
        0xee, 0x0d, 0x86, 0x93, 0xdf, 0x26, 0x3c, 0x66,
        0x9a, 0xd3, 0xe8, 0xe0, 0xd4, 0x3f, 0xaf, 0x58,
        0x7c, 0x7d, 0xf5, 0x3c, 0xef, 0x1f, 0x5b, 0xca,
        0x7f, 0xbf, 0xfb, 0x3e, 0xcf, 0xfe, 0xca, 0xa2,
        0xed, 0xbf, 0x77, 0xcf, 0x9e, 0xfc, 0xe4, 0xb3,
        0x69, 0xdf, 0x62, 0x8d, 0x53, 0x72, 0xf5, 0x71,
        0xfb, 0xb2, 0xd2, 0x05, 0x19, 0x20, 0x40, 0x60,
        0xc7, 0x9b, 0xe4, 0x99, 0x53, 0x92, 0x1b, 0x56,
        0x44, 0x3f, 0x59, 0xfc, 0xd1, 0x14, 0x26, 0xb8,
        0x2b, 0x72, 0xf1, 0xbc, 0xb0, 0xc5, 0x0d, 0x8f,
        0xb7, 0x18, 0x4f, 0x61, 0x86, 0x8a, 0x35, 0x6d,
        0x7f, 0xf5, 0x7d, 0xd6, 0xd5, 0xd6, 0x86, 0xbf,
        0x49, 0xf3, 0x4e, 0x31, 0x42, 0xc5, 0x0e, 0x66,
        0xcb, 0x97, 0x35, 0x67, 0x71, 0x6f, 0xd0, 0xbc,
        0xb6, 0xb6, 0x53, 0x0e, 0xa6, 0x77, 0xcf, 0x5b,
        0xa3, 0xce, 0xd3, 0xba, 0x0e, 0xdb, 0x4f, 0xb8,
        0x27, 0x5b, 0x42, 0xc5, 0x14, 0x2a, 0x36, 0xbb,
        0xd9, 0xea, 0x6e, 0x67, 0xb8, 0x59, 0x78, 0x4b,
        0x12, 0xa1, 0x39, 0xfa, 0x6b, 0xf5, 0xd9, 0x57,
        0x93, 0x69, 0x6c, 0x60, 0xb5, 0xd5, 0x9b, 0x4d,
        0x9f, 0x0c, 0x0e, 0x3c, 0xd8, 0x7b, 0x62, 0x7f,
        0xf6, 0x5b, 0x0e, 0x06, 0x86, 0x07, 0xfb, 0x77,
        0xda, 0x56, 0xee, 0xdb, 0xb1, 0xe7, 0x57, 0xf5,
        0xf7, 0x39, 0xff, 0x98, 0xfe, 0x9a, 0xf3, 0x9f,
        0x9b, 0xdf, 0xcb, 0xc8, 0x00, 0x00, 0x1a, 0x15,
        0x9d, 0x48, 0x72, 0x01, 0x00, 0x00
    )),
    '1G': bytearray((
        0x1f, 0x8b, 0x08, 0x00, 0xcb, 0x77, 0x62, 0x59,
        0x02, 0x03, 0x01, 0x26, 0x01, 0xd9, 0xfe, 0x1f,
        0x8b, 0x08, 0x00, 0xcb, 0x77, 0x62, 0x59, 0x02,
        0x03, 0x93, 0xef, 0xe6, 0x60, 0x38, 0x5d, 0x9e,
        0x14, 0xc9, 0xc4, 0xfc, 0xf6, 0xee, 0x42, 0xbe,
        0xdf, 0x01, 0x92, 0xed, 0x0f, 0xeb, 0x33, 0x59,
        0x1d, 0xb7, 0xcc, 0x9d, 0x91, 0xc5, 0xb1, 0xb7,
        0x67, 0x96, 0xda, 0xda, 0x95, 0xeb, 0x24, 0x9a,
        0x14, 0x66, 0x09, 0xbd, 0x31, 0x29, 0xf2, 0x9d,
        0xa5, 0xc9, 0x63, 0xde, 0xc8, 0xb6, 0x99, 0x9b,
        0x61, 0x2b, 0x8b, 0xbb, 0x93, 0xd5, 0x1d, 0xbd,
        0x06, 0x05, 0xb5, 0x65, 0x52, 0x5c, 0x6f, 0x6d,
        0x15, 0xfc, 0x3e, 0xd9, 0xbc, 0x7a, 0x11, 0xfe,
        0xbf, 0x68, 0x5f, 0xfc, 0x9f, 0x7f, 0xcb, 0xed,
        0xff, 0x7d, 0xdb, 0x7d, 0xff, 0xcf, 0x2b, 0xf5,
        0x8f, 0xfb, 0xff, 0x09, 0xb9, 0xda, 0xd7, 0xfd,
        0x99, 0xf1, 0xef, 0xc3, 0x7c, 0xfb, 0xbf, 0xbf,
        0x97, 0xdb, 0xff, 0x66, 0x64, 0x80, 0x00, 0x96,
        0xbc, 0x5f, 0xcf, 0x65, 0xde, 0x27, 0x37, 0xc8,
        0x3f, 0xdd, 0x56, 0xf2, 0x57, 0x1f, 0x2a, 0xda,
        0x70, 0xa1, 0x37, 0x72, 0x96, 0xcc, 0xe2, 0x86,
        0x52, 0x8d, 0x28, 0x4b, 0xa8, 0x3a, 0x85, 0x8a,
        0xef, 0xbb, 0x4e, 0xf5, 0xcb, 0x33, 0xd9, 0x6d,
        0xcf, 0x56, 0x62, 0x87, 0xe9, 0x7d, 0xff, 0xa7,
        0xd6, 0xfc, 0xb8, 0xd8, 0x83, 0x9d, 0xb6, 0x7e,
        0xe2, 0xb6, 0x70, 0x75, 0xeb, 0x2d, 0xfb, 0xbe,
        0xe9, 0x3a, 0xec, 0xd4, 0x8d, 0xd5, 0x87, 0xab,
        0xcb, 0x3f, 0x73, 0x29, 0xe5, 0x3e, 0x93, 0xcf,
        0xeb, 0x80, 0x2d, 0x45, 0x50, 0x21, 0x87, 0x0f,
        0xef, 0x4a, 0xa7, 0xca, 0xbb, 0x8f, 0x1a, 0x37,
        0x6a, 0xdc, 0xa8, 0x71, 0xa3, 0xc6, 0x8d, 0x1a,
        0x37, 0x6a, 0xdc, 0xa8, 0x71, 0xa3, 0xc6, 0x8d,
        0x1a, 0x47, 0x82, 0x71, 0xff, 0x22, 0xc2, 0x9f,
        0xee, 0x63, 0x3d, 0xf1, 0x7f, 0xdf, 0xdf, 0xc7,
        0xcf, 0x8f, 0xf3, 0x33, 0xfe, 0x77, 0xaf, 0xfd,
        0xf3, 0x7c, 0xff, 0xbf, 0x6f, 0xd7, 0xff, 0x57,
        0x9b, 0xfc, 0x67, 0x55, 0x7e, 0xf9, 0x40, 0x6d,
        0xea, 0x33, 0x7e, 0x06, 0x00, 0x9f, 0x2f, 0x0c,
        0x99, 0x54, 0x0a, 0x00, 0x00, 0x3a, 0x3d, 0x97,
        0x8a, 0x26, 0x01, 0x00, 0x00
    )),
    '10G': bytearray((
        0x1f, 0x8b, 0x08, 0x00, 0x12, 0x79, 0x62, 0x59,
        0x02, 0x03, 0xad, 0xd2, 0xfb, 0x3f, 0x13, 0x08,
        0x00, 0x00, 0x70, 0x8f, 0xab, 0xa9, 0xdd, 0x68,
        0x68, 0xcd, 0x32, 0xfa, 0xf4, 0x9a, 0x57, 0x65,
        0x79, 0xd4, 0x1a, 0xab, 0x33, 0x0b, 0x09, 0x33,
        0x43, 0x4c, 0x14, 0x2e, 0xa3, 0xcd, 0x65, 0xb2,
        0xa1, 0xcb, 0x42, 0x75, 0x65, 0x72, 0x8d, 0xe2,
        0x3c, 0xb6, 0xb2, 0x74, 0x53, 0xdd, 0x66, 0x5e,
        0x3b, 0x11, 0x79, 0x15, 0xd9, 0x79, 0xb4, 0x55,
        0x9a, 0xb6, 0x56, 0x0c, 0x37, 0xcb, 0x63, 0x9e,
        0x59, 0xba, 0xee, 0x7f, 0xb8, 0xcf, 0xfd, 0xf8,
        0xfd, 0xfd, 0x6b, 0xcb, 0x32, 0x31, 0x30, 0xcf,
        0x88, 0x8d, 0x30, 0x32, 0x9e, 0x96, 0x91, 0x8e,
        0x17, 0x25, 0x40, 0x01, 0x73, 0xe2, 0xa1, 0xef,
        0x9d, 0x3a, 0x3b, 0x4f, 0xa4, 0x64, 0xa7, 0xfc,
        0x06, 0x5d, 0x9f, 0xf8, 0xb2, 0x29, 0xc0, 0x99,
        0x36, 0x52, 0xd8, 0x6f, 0x78, 0x14, 0xfa, 0xdc,
        0x4f, 0x80, 0xf3, 0xd8, 0xe6, 0xe0, 0x05, 0x56,
        0xe3, 0x0b, 0xe0, 0xf2, 0x39, 0x23, 0xf0, 0xee,
        0x48, 0x77, 0x57, 0xcb, 0xb1, 0x76, 0x14, 0xd4,
        0x27, 0xd1, 0x07, 0xd8, 0xd0, 0x77, 0xd0, 0xb7,
        0x0b, 0x7f, 0x9e, 0x68, 0x47, 0xd5, 0x6c, 0x34,
        0xb7, 0x1b, 0x32, 0xf2, 0xca, 0x8e, 0x44, 0x43,
        0xde, 0xad, 0xb4, 0xbc, 0x9d, 0xde, 0x4b, 0xd7,
        0xfd, 0x5c, 0x12, 0xd4, 0xc6, 0x7c, 0x3f, 0x99,
        0x71, 0x47, 0xa5, 0x8d, 0xa6, 0xe4, 0xa6, 0xc6,
        0x73, 0xaa, 0xc0, 0x7f, 0x4c, 0xa8, 0xb9, 0xcb,
        0x92, 0x60, 0x39, 0x2e, 0xe8, 0x96, 0x63, 0x37,
        0xfa, 0x8a, 0x21, 0x88, 0xcf, 0xe1, 0xd1, 0x93,
        0xbf, 0x79, 0xea, 0xeb, 0xbd, 0x1e, 0xb5, 0x4f,
        0xfd, 0x43, 0x84, 0xa0, 0xfa, 0xec, 0x73, 0x16,
        0xaa, 0x28, 0x8b, 0xc1, 0x6e, 0xf7, 0xcb, 0xea,
        0x66, 0x25, 0xd9, 0x90, 0xe5, 0x7d, 0xb1, 0xbf,
        0x9a, 0x39, 0x6a, 0xb4, 0x40, 0xe6, 0x95, 0xa0,
        0x10, 0xa2, 0x19, 0xac, 0xa5, 0xe1, 0x98, 0x2c,
        0x09, 0x77, 0x2d, 0x71, 0xa9, 0x29, 0x51, 0xa9,
        0xb4, 0xfc, 0x1a, 0x49, 0xfa, 0xa0, 0xe8, 0x02,
        0xd9, 0x57, 0x6f, 0x2e, 0x2d, 0x56, 0x06, 0xe8,
        0xf3, 0x8c, 0xee, 0x6d, 0x9e, 0xe9, 0x67, 0x1c,
        0xca, 0xc8, 0x7d, 0x87, 0x79, 0xcf, 0x72, 0x84,
        0x92, 0x2c, 0xac, 0x5d, 0xa8, 0xc8, 0x70, 0x44,
        0x91, 0xd6, 0xc5, 0xc3, 0xdf, 0x64, 0x55, 0xe9,
        0xd0, 0x47, 0x2a, 0xb6, 0x2d, 0x75, 0x09, 0x07,
        0x95, 0x78, 0x8c, 0x1d, 0xba, 0x7d, 0x45, 0x38,
        0x41, 0x88, 0x98, 0x04, 0x76, 0xbd, 0x87, 0x3d,
        0xfc, 0x7c, 0xef, 0x83, 0xfc, 0x04, 0x20, 0x55,
        0x10, 0xc3, 0x1e, 0x0b, 0xaf, 0xf0, 0xce, 0x54,
        0x38, 0x72, 0xe6, 0x9f, 0xf1, 0x96, 0xac, 0x10,
        0xf1, 0x97, 0x8d, 0xb7, 0x87, 0x6e, 0xec, 0xa1,
        0x25, 0x03, 0xbf, 0x11, 0x62, 0xa2, 0xc5, 0x71,
        0x45, 0x39, 0xab, 0x0f, 0x5a, 0x77, 0xc1, 0x5a,
        0x28, 0x4f, 0xdc, 0x8e, 0x73, 0xd3, 0x07, 0x3d,
        0x5b, 0xc1, 0xb8, 0xc6, 0x1f, 0x36, 0x7b, 0x7a,
        0x8c, 0x46, 0x34, 0xee, 0x5e, 0x5a, 0x9f, 0xa7,
        0x67, 0xee, 0xa1, 0x1c, 0xeb, 0x1c, 0x76, 0x08,
        0x31, 0xda, 0x99, 0x9e, 0x4a, 0xbd, 0xb5, 0x17,
        0x0f, 0x00, 0xc8, 0x9f, 0x93, 0x57, 0x6d, 0xec,
        0x46, 0x9a, 0xb8, 0xcc, 0x39, 0x6b, 0x3f, 0xc6,
        0x7d, 0xe2, 0x36, 0x5c, 0xf0, 0xc5, 0xdb, 0xea,
        0xaa, 0xfc, 0x73, 0x4c, 0x64, 0xeb, 0x45, 0x03,
        0xdc, 0xc9, 0x29, 0xe8, 0x60, 0x46, 0x13, 0xff,
        0xaf, 0x4b, 0xa4, 0x90, 0x09, 0xf3, 0x0b, 0x05,
        0x0e, 0x4f, 0x7b, 0x05, 0x75, 0xc2, 0x61, 0x99,
        0x04, 0x4f, 0x2c, 0xdb, 0x4a, 0x5b, 0xc1, 0x20,
        0x1f, 0x31, 0x9e, 0x46, 0xe5, 0xf2, 0x50, 0x58,
        0x5d, 0xbf, 0xdf, 0x67, 0xa6, 0xd0, 0x94, 0x55,
        0xbc, 0xa6, 0x61, 0x64, 0x0f, 0x70, 0x75, 0x8c,
        0xaf, 0x3b, 0x5e, 0x47, 0x01, 0x4f, 0x8e, 0x3b,
        0xad, 0x41, 0xac, 0xfc, 0xa0, 0x48, 0xfc, 0x97,
        0x60, 0xd7, 0x5a, 0xd6, 0x05, 0x72, 0xfe, 0xa6,
        0xea, 0xb6, 0x7a, 0x51, 0x0e, 0x8f, 0x23, 0xdb,
        0x53, 0xce, 0xd9, 0x39, 0xbe, 0x1f, 0x26, 0x22,
        0xcf, 0x66, 0x24, 0xd8, 0x84, 0xae, 0x49, 0x9f,
        0x61, 0x4e, 0xd7, 0x3c, 0x9e, 0x60, 0x5b, 0xb0,
        0x51, 0x59, 0xc3, 0x5b, 0x6b, 0x90, 0x85, 0x88,
        0xe0, 0x45, 0x8b, 0xf1, 0x9b, 0x41, 0xe6, 0x6d,
        0x49, 0x3a, 0xc7, 0x8b, 0xee, 0x79, 0x0e, 0x52,
        0x72, 0x39, 0xe7, 0x93, 0x66, 0x1e, 0x9d, 0x83,
        0x0b, 0x6a, 0x64, 0xc7, 0xab, 0x9b, 0x6e, 0x08,
        0x4a, 0x48, 0xb5, 0x7b, 0xde, 0x7c, 0x22, 0xa5,
        0x47, 0x0e, 0x44, 0xbf, 0x40, 0x9c, 0xe6, 0x87,
        0x25, 0xf1, 0x6b, 0x16, 0xce, 0x61, 0xcf, 0x1e,
        0x9e, 0xfc, 0xae, 0xb2, 0x5a, 0xcc, 0xe9, 0xbc,
        0x77, 0xb5, 0xd9, 0xba, 0xa6, 0xba, 0x8b, 0xd7,
        0x1f, 0xa7, 0xda, 0xc5, 0xa6, 0x5b, 0xb1, 0x9a,
        0x13, 0xc9, 0xac, 0xbc, 0x8f, 0x2b, 0x4b, 0x2e,
        0xa7, 0x47, 0x29, 0x60, 0x30, 0x3a, 0x0d, 0x7f,
        0x07, 0x12, 0x98, 0x80, 0x50, 0x63, 0xb4, 0xe7,
        0xb1, 0xc1, 0x5f, 0x91, 0x75, 0xf9, 0x51, 0x27,
        0xa5, 0x76, 0xa8, 0x7c, 0x5c, 0xdc, 0x84, 0xed,
        0xfc, 0xb5, 0xc3, 0x6b, 0x2c, 0xa5, 0xff, 0xbe,
        0x53, 0x80, 0x4f, 0x97, 0xe0, 0x22, 0x63, 0x7a,
        0xbb, 0xe9, 0x5b, 0x43, 0xf4, 0xff, 0x8c, 0x15,
        0x95, 0x48, 0x56, 0x3a, 0x31, 0xde, 0x2f, 0x56,
        0xd6, 0xcf, 0x42, 0x1e, 0x50, 0xf2, 0x27, 0xe9,
        0x26, 0x21, 0xa3, 0x1b, 0xe2, 0x6c, 0x30, 0xf3,
        0xd4, 0xa2, 0x98, 0x06, 0xea, 0x8b, 0xc5, 0xc7,
        0xdb, 0x53, 0x1e, 0x66, 0x1e, 0xc1, 0x7f, 0x64,
        0xfc, 0xb2, 0x9a, 0x84, 0x10, 0xff, 0xe3, 0xfa,
        0x44, 0xa9, 0x87, 0xa3, 0x13, 0xd0, 0x1d, 0x99,
        0xa4, 0xc1, 0x03, 0xb2, 0x15, 0x53, 0x98, 0x8f,
        0x42, 0xa5, 0xb8, 0x0b, 0x92, 0x05, 0xcc, 0x1b,
        0x5a, 0xc4, 0x58, 0x1d, 0x2e, 0xbf, 0xe1, 0xfe,
        0x8a, 0xdd, 0x5b, 0xad, 0xd9, 0x96, 0x2c, 0xa9,
        0x71, 0xbe, 0x1a, 0x31, 0xf3, 0xec, 0xe8, 0x05,
        0xe4, 0x5c, 0xe7, 0xb5, 0x03, 0xdc, 0xb3, 0x77,
        0x31, 0x75, 0xae, 0x82, 0xb2, 0x59, 0xe9, 0x99,
        0xde, 0x0d, 0xf0, 0x0a, 0xcd, 0xeb, 0x4c, 0x49,
        0xbb, 0x4a, 0x5f, 0xf2, 0x9c, 0x39, 0xd8, 0x03,
        0x9a, 0x09, 0x9c, 0x6d, 0xa0, 0xfc, 0x4d, 0xc5,
        0x91, 0xb0, 0x0d, 0x39, 0xa7, 0x10, 0x85, 0x4f,
        0x96, 0xbd, 0x9e, 0x6a, 0x8c, 0x15, 0xcb, 0xe4,
        0x3e, 0x39, 0xf6, 0xa8, 0x29, 0xe1, 0x91, 0x04,
        0x7f, 0x66, 0x63, 0x91, 0xae, 0xb6, 0xb0, 0xa1,
        0x02, 0x2c, 0x69, 0x37, 0xfb, 0x69, 0xb9, 0x71,
        0x51, 0x26, 0x4f, 0xc8, 0xb2, 0xec, 0x8e, 0xe5,
        0x58, 0x7b, 0x8e, 0x76, 0x75, 0x6f, 0xb1, 0x1f,
        0x03, 0x0a, 0x2b, 0x55, 0xb4, 0x28, 0x78, 0xb2,
        0xf0, 0xf2, 0x75, 0xfe, 0xc2, 0x8e, 0x9b, 0x23,
        0x4e, 0x95, 0x61, 0xbd, 0x1f, 0xc6, 0x60, 0xfc,
        0x91, 0xdc, 0x21, 0x8b, 0x50, 0x10, 0x97, 0x17,
        0x40, 0xc0, 0x92, 0xcc, 0x9c, 0xe9, 0xbc, 0xc0,
        0xfd, 0x4c, 0x41, 0xcb, 0x40, 0x4f, 0xda, 0x59,
        0x92, 0x97, 0xa8, 0x23, 0x47, 0x18, 0x6d, 0xa3,
        0x98, 0x2b, 0xf3, 0xb5, 0x98, 0x6e, 0x9f, 0xf1,
        0x16, 0x96, 0x1c, 0x18, 0x92, 0x4b, 0xef, 0xeb,
        0x1c, 0x16, 0xbd, 0xd3, 0xf6, 0x95, 0xd9, 0xfb,
        0xab, 0x93, 0x22, 0xa9, 0xd8, 0x75, 0x53, 0xde,
        0x07, 0x69, 0xe9, 0x97, 0x06, 0xc2, 0x7e, 0x2c,
        0xa0, 0xd5, 0x76, 0x28, 0xf4, 0xcd, 0x83, 0x6a,
        0xd4, 0xd4, 0xc8, 0xed, 0x61, 0x11, 0x3a, 0xc2,
        0x79, 0xa7, 0xff, 0x83, 0x51, 0xef, 0xb0, 0xf9,
        0x4d, 0x99, 0xbc, 0x08, 0x09, 0x32, 0x1e, 0xa2,
        0x41, 0x8e, 0xdf, 0xb4, 0x64, 0x13, 0x90, 0xae,
        0x6d, 0x21, 0xc4, 0xda, 0xc0, 0x83, 0x5b, 0xae,
        0x83, 0xc2, 0x1e, 0x62, 0x5e, 0xc2, 0x28, 0x2d,
        0xee, 0x03, 0xdd, 0xe2, 0xae, 0x57, 0x93, 0x3a,
        0x37, 0xf5, 0x75, 0xf1, 0x91, 0x2c, 0xa3, 0x4c,
        0x1e, 0xdc, 0xe9, 0x58, 0x0a, 0x40, 0xe7, 0x34,
        0xc9, 0x5d, 0xcf, 0x96, 0xba, 0x55, 0xa9, 0x4e,
        0x6c, 0xef, 0x11, 0x20, 0xc3, 0x5a, 0x6b, 0x3b,
        0xf4, 0x90, 0x72, 0x72, 0x94, 0x56, 0xb1, 0x0e,
        0x23, 0x86, 0xb7, 0x55, 0xfa, 0x17, 0x07, 0x4a,
        0xe1, 0x82, 0xc2, 0xc6, 0xe6, 0xca, 0x02, 0x63,
        0xd4, 0x1d, 0x47, 0x13, 0x5b, 0x7f, 0xae, 0xe0,
        0x14, 0xc7, 0x77, 0xdd, 0x47, 0x27, 0xa9, 0x30,
        0x3c, 0xeb, 0x2a, 0x8d, 0xe2, 0x9c, 0xf6, 0x66,
        0x41, 0xef, 0xeb, 0x25, 0xe2, 0x16, 0x50, 0x7d,
        0x8a, 0xf9, 0x15, 0x5b, 0x36, 0xd5, 0x57, 0x63,
        0x17, 0x5c, 0x01, 0xaf, 0x90, 0xff, 0xf1, 0xc2,
        0x37, 0x06, 0x9d, 0x27, 0xef, 0x6f, 0x01, 0x2a,
        0xf1, 0xa9, 0x01, 0xda, 0x2f, 0x20, 0x02, 0x38,
        0x70, 0xa9, 0x4f, 0x45, 0x26, 0x42, 0xa0, 0xb7,
        0x7e, 0x27, 0x84, 0xc6, 0x6b, 0xa7, 0x17, 0x5e,
        0xfc, 0x99, 0x12, 0xa5, 0x50, 0x49, 0x88, 0x4a,
        0x64, 0x69, 0xac, 0x81, 0xc1, 0xbf, 0xf3, 0xc7,
        0x37, 0xff, 0x18, 0x05, 0x00, 0x00
    )),
}


class GzipBombResponse(flask.Response):
    """Response containing GzipBomb."""

    #: Accaptable content sizes (rounds, data)
    _gzipData = {
        #: 1 kB
        '1k':   (1, rawdata['1k']),
        #: 10 kB
        '10k':  (1, rawdata['10k']),
        #: 100 kB
        '100k': (2, rawdata['100k']),
        #: 1 MB
        '1M':   (2, rawdata['1M']),
        #: 10 MB
        '10M':  (2, rawdata['10M']),
        #: 100 MB
        '100M': (3, rawdata['100M']),
        #: 1 GB
        '1G':   (3, rawdata['1G']),
        #: 10 GB
        '10G':  (4, rawdata['10G']),
    }

    def __init__(self, *args, **kwargs):
        """
        GzipBombResponse initializer.
        Accepts the same arguments as flask.Response class with the
        addition of *size* parameter with predefined possible values:
            '1k', '10k', '100k', '1M', '10M', '100M', '1G', '10G'
        with *k*, *M* and *G* denoting kilobyte, megabyte and gigabyte.
        Passing any other value will raise a KeyError.
        """
        size = kwargs.pop('size', '10M')

        super(flask.Response, self).__init__(*args, **kwargs)
        self.size = size

    @property
    def size(self):
        """Get decompressed content size."""
        return self._size

    @size.setter
    def size(self, size):
        """Set decompressed content size."""
        self._size = size

        rounds, self.data = self._gzipData[self._size]

        self.headers['Content-Encoding'] = ','.join(['gzip'] * rounds)
        self.headers['Content-Length'] = len(self.data)


# Create the application object
app = flask.Flask(__name__)
# Create a DB connection
db = sqlite3.connect(DATABASE, check_same_thread=False)
# Create a cursor
c = db.cursor()
# Create a table
c.execute("""CREATE TABLE IF NOT EXISTS visitors (
            uuid TEXT,
            ip TEXT,
            time TEXT,
            ua TEXT,
            referrer TEXT,
            ext TEXT,
            header TEXT)""")
# Commit the changes
db.commit()
# Close the DB connection
db.close()


@app.route('/clean')
# DB Cleanup
# Arguments: secret, secret is the secret key
#            keep, number of days to keep
#            vacuum, if 1, vacuum the DB
def clean():
    # Use default SECRET
    SECRET = SECRET_KEY
    # Get the secret
    secret = flask.request.args.get('secret', None)
    # Check if the secret is correct
    if secret != SECRET:
        return permission_denied()
    # Get the number of days to keep
    keep = flask.request.args.get('keep', None)
    # Check if the number of days to keep is valid
    if keep is None or not keep.isdigit():
        return 'Invalid keep'
    # Convert the number of days to keep to an integer
    keep = int(keep)
    # Get the current time
    now = time.time()
    # Get the time of the day
    today = time.strftime('%Y-%m-%d', time.localtime(now))
    # Get the time of the day minus the number of days to keep
    yesterday = time.strftime('%Y-%m-%d', time.localtime(now - (86400 * keep)))
    # Create a DB connection
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    # Create a cursor
    c = db.cursor()
    # Delete all entries older than the number of days to keep
    c.execute("DELETE FROM visitors WHERE time < ?", (yesterday,))
    # Commit the changes
    db.commit()
    # Vacuum the DB
    if flask.request.args.get('vacuum', None) == '1':
        c.execute("VACUUM")
    # Close the DB connection
    db.close()
    # Return a success message
    return 'Cleaned'


@app.route("/append")
# Append a new visitor to the DB, any method can be used
def append():
    # Get the data from the request
    try:
        uuid = str(flask.request.values.get('uuid'))
    except:
        uuid = 'None'
    try:
        ext = str(flask.request.values.get('ext'))
    except:
        ext = 'None'
    try:
        # Overide if Cf-Connecting-Ip is present
        if flask.request.headers.get('Cf-Connecting-Ip'):
            ip = str(flask.request.headers.get('Cf-Connecting-Ip'))
        elif flask.request.headers.get('X-Forwarded-For'):
            ip = str(flask.request.headers["X-Forwarded-For"])
        else:
            ip = str(flask.request.remote_addr)
    except:
        ip = 'None'
    try:
        ua = str(flask.request.headers["User-Agent"])
    except:
        ua = 'None'
    try:
        referrer = str(flask.request.headers["Referer"])
    except:
        referrer = 'None'
    try:
        header = str(flask.request.headers)
    except:
        header = 'None'
    currtime = time.strftime("%Y-%m-%d %H:%M:%S")
    # Create a DB connection
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    # Create a cursor
    c = db.cursor()
    # Insert the data
    c.execute("""INSERT INTO visitors VALUES (?,?,?,?,?,?,?)""",
              (uuid, ip, currtime, ua, referrer, ext, header))
    # Commit the changes
    db.commit()
    # Close the DB connection
    db.close()
    # Make a response
    # If debug
    if app.debug:
        resp = flask.make_response(flask.jsonify(
            {"uuid": uuid, "ip": ip, "time": currtime, "ua": ua, "referrer": referrer, "ext": ext, "header": header}), 200)
        # Allow Cross Origin Resource Sharing
        resp.headers['Access-Control-Allow-Origin'] = "*"
    else:
        resp = flask.make_response("{}", 200)
        # Mime javascript
        resp.mimetype = 'application/javascript'
        # Allow Cross Origin Resource Sharing
        resp.headers['Access-Control-Allow-Origin'] = "*"
    # Return the data
    return resp


@app.route("/post", methods=['POST'])
# Append a new visitor to the DB, using POST
def post():
    # Get the data from the request
    try:
        uuid = str(flask.request.form['uuid'])
    except:
        uuid = 'None'
    try:
        ext = str(flask.request.form['ext'])
    except:
        ext = 'None'
    try:
        # Overide if Cf-Connecting-Ip is present
        if flask.request.headers.get('Cf-Connecting-Ip'):
            ip = str(flask.request.headers.get('Cf-Connecting-Ip'))
        elif flask.request.headers.get('X-Forwarded-For'):
            ip = str(flask.request.headers["X-Forwarded-For"])
        else:
            ip = str(flask.request.remote_addr)
    except:
        ip = 'None'
    try:
        ua = str(flask.request.headers["User-Agent"])
    except:
        ua = 'None'
    try:
        referrer = str(flask.request.headers["Referer"])
    except:
        referrer = 'None'
    try:
        header = str(flask.request.headers)
    except:
        header = 'None'
    currtime = time.strftime("%Y-%m-%d %H:%M:%S")
    # Create a DB connection
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    # Create a cursor
    c = db.cursor()
    # Insert the data
    c.execute("""INSERT INTO visitors VALUES (?,?,?,?,?,?,?)""",
              (uuid, ip, currtime, ua, referrer, ext, header))
    # Commit the changes
    db.commit()
    # Close the DB connection
    db.close()
    # Make a response
    # If debug
    if app.debug:
        resp = flask.make_response(flask.jsonify(
            {"uuid": uuid, "ip": ip, "time": currtime, "ua": ua, "referrer": referrer, "ext": ext, "header": header}), 200)
        # Allow Cross Origin Resource Sharing
        resp.headers['Access-Control-Allow-Origin'] = "*"
    else:
        resp = flask.make_response("{}", 200)
        # Mime javascript
        resp.mimetype = 'application/javascript'
        # Allow Cross Origin Resource Sharing
        resp.headers['Access-Control-Allow-Origin'] = "*"
    # Return the data
    return resp


@app.route("/")
# Return the index page
def index():
    # Make a response
    # If in debug mode, return this
    if app.debug:
        resp = flask.make_response("""<html>
        <head>
        <title>Visitor Logger</title>
        </head>
        <body>
        <h1>Visitor Logger</h1>
        <p>This is a simple visitor logger for the website.</p>
        <p>You can use the following endpoints:</p>
        <ul>
        <li>/append - Append a new visitor to the DB</li>
        <li>/post - Append a new visitor to the DB using POST</li>
        <li>/clean - Clean the DB</li>
        <li>/getdb - Get the DB</li>
        <li>/query - Query the DB</li>
        <li>/report - Create HTML report</li>
        <li>/js - Get the JS file</li>
        </ul>
        </body>
        </html>""")
    else:
        # 418 I'm a teapot
        resp = flask.make_response("I'm a teapot", 418)
    # Allow Cross Origin Resource Sharing
    resp.headers['Access-Control-Allow-Origin'] = "*"
    # Return the data
    return resp


@app.route("/getdb", methods=['GET'])
# Return the DB file
# Check SECRET
def getdb():
    # Make a response
    SECRET = SECRET_KEY
    if flask.request.values.get('secret') == SECRET:
        resp = flask.make_response(open(DATABASE, 'rb').read())
        resp.headers['Content-Type'] = 'application/octet-stream'
        resp.headers['Content-Disposition'] = 'attachment; filename=db.sqlite'
        # Allow Cross Origin Resource Sharing
        resp.headers['Access-Control-Allow-Origin'] = "*"
        # Return the data
        return resp
    else:
        return permission_denied()


@app.route("/query", methods=['GET'])
# Query DB for insert time
# Arguments: secret, hours
def query():
    # Make a response
    SECRET = SECRET_KEY
    if flask.request.values.get('secret') == SECRET:
        # Get the data from the request
        try:
            hours = int(flask.request.values.get('hours'))
        except:
            hours = 1
        # Create a DB connection
        db = sqlite3.connect(DATABASE, check_same_thread=False)
        # Create a cursor
        c = db.cursor()
        # Query the DB
        c.execute(
            """SELECT * FROM visitors WHERE time > datetime('now', '-%s hours')""" % hours)
        # Get the data
        data = c.fetchall()
        # Close the DB connection
        db.close()
        # Make a response
        resp = flask.make_response(flask.jsonify(data), 200)
        # Allow Cross Origin Resource Sharing
        resp.headers['Access-Control-Allow-Origin'] = "*"
        # Return the data
        return resp
    else:
        return permission_denied()


@app.route("/report", methods=['GET'])
# Create HTML report
# Arguments: secret, hours
def report():
    # Make a response
    SECRET = SECRET_KEY
    if flask.request.values.get('secret') == SECRET:
        # Get the data from the request
        try:
            hours = int(flask.request.values.get('hours'))
        except:
            hours = 1
        # Header
        html = '<html><head>'
        # charset
        html += '<meta charset="utf-8">'
        # title
        html += '<title>Visitor Logger</title>'
        # Append Style to the HTML report
        html += '<style>table, th, td {border: 1px solid black;border-collapse: collapse;}</style>'
        # Append JS filter to the HTML report
        html += '<script>function filterTable() {var input, filter, table, tr, td, i;input = document.getElementById("myInput");filter = input.value.toUpperCase();table = document.getElementById("myTable");tr = table.getElementsByTagName("tr");for (i = 0; i < tr.length; i++) {td = tr[i].getElementsByTagName("td")[0];if (td) {if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {tr[i].style.display = "";} else {tr[i].style.display = "none";}}} }</script>'
        # Body
        html += '</head><body>'
        # Title
        html += '<h1>Visitor Logger</h1>'
        # Append the filter input to the HTML report
        html += '<input type="text" id="myInput" onkeyup="filterTable()" placeholder="Search for UUID..">'
        # Append the table to the HTML report
        html += '<table id="myTable"><tr><th>UUID</th><th>IP</th><th>Time</th><th>User Agent</th><th>Referrer</th><th>Extension</th><th>Header</th></tr>'
        # Create a DB connection
        db = sqlite3.connect(DATABASE, check_same_thread=False)
        # Create a cursor
        c = db.cursor()
        # Query the DB
        c.execute(
            """SELECT * FROM visitors WHERE time > datetime('now', '-%s hours')""" % hours)
        # Get the data
        data = c.fetchall()
        # Close the DB connection
        db.close()
        # Loop through the data
        for row in data:
            # Append the row to the HTML report
            html += '<tr><td>' + str(row[0]) + '</td><td>' + str(row[1]) + '</td><td>' + str(row[2]) + '</td><td>' + str(
                row[3]) + '</td><td>' + str(row[4]) + '</td><td>' + str(row[5]) + '</td><td>' + str(row[6]) + '</td></tr>'
        # Append the closing tags to the HTML report
        html += '</table></body></html>'
        # Make a response
        resp = flask.make_response(html)
        # Allow Cross Origin Resource Sharing
        resp.headers['Access-Control-Allow-Origin'] = "*"
        # Return the data
        return resp
    else:
        return permission_denied()


@app.route("/js", methods=['GET'])
# Return the JS file
# Replace apiURL with API_URL
def js():
    # Read the JS file
    js = open(JS, 'r').read()
    # Replace the API URL
    js = js.replace('http://localhost/append', API_URL)
    # Make a response
    resp = flask.make_response(js)
    resp.headers['Content-Type'] = 'application/javascript'
    # Allow Cross Origin Resource Sharing
    resp.headers['Access-Control-Allow-Origin'] = "*"
    # Return the data
    return resp


@app.route("/favicon.ico")
# Return blank favicon
def favicon():
    # Make a response
    resp = flask.make_response()
    # Return the data
    return resp


# Handle any other requests(404)
# Anti-Attack with GzipBomb
@app.errorhandler(404)
def not_found(error):
    return permission_denied()


# Run the application
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
# End of file
