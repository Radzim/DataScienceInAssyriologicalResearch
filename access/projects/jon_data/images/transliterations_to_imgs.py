import os
import fitz
import glob

# files = glob.glob('transliterations pdfs/**/*.pdf')
#
# for i in range(900, len(files)):
#     try:
#         pdf_file = files[i]
#         print(i, '/', len(files), pdf_file)
#         pages = fitz.open(pdf_file)
#         if len(pages) > 1:
#             for i in range(len(pages)):
#                 pix = pages[i].get_pixmap(matrix=fitz.Matrix(5,5))
#                 jpg_file = 'transliterations_jpgs/' + pdf_file[21:-4] + "_" + str(i + 1) + ".jpg"
#                 os.makedirs(os.path.dirname(jpg_file), exist_ok=True)
#                 pix.save(jpg_file)
#     except:
#         print('\n\nFAILED\n\n', files[i], '\n\n')