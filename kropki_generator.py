import os
import sys
import json
import argparse
import urllib.request as ul
from PIL import Image


def download_data():
    for i in range(1, 130):
        empty_url = "https://www.janko.at/Raetsel/Sudoku-Kropki/{:03d}.{}.gif".format(i, 'c')
        solution_url = "https://www.janko.at/Raetsel/Sudoku-Kropki/{:03d}.{}.gif".format(i, 'd')
        empty_filename = "data/{:03d}.raw.gif".format(i)
        solution_filename = "data/{:03d}.solution.gif".format(i)
        print("{}".format(empty_url))
        with ul.urlopen(empty_url) as response, open(empty_filename, 'wb') as out:
            data = response.read()  # a `bytes` object
            out.write(data)
        with ul.urlopen(solution_url) as response, open(solution_filename, 'wb') as out:
            data = response.read()
            out.write(data)


def parse_raw(filename, verbose=False, check_image=False):
    # Color to text
    c2t = {
        (0, 0, 0): "black", (255, 255, 255): "white", (231, 231, 231): "white",
        (153, 153, 153): "grey", (8, 8, 8): "border"
    }
    im = Image.open(filename)
    rgb_im = im.convert('RGB')
    dot_list = []
    xindices, yindices = None, None
    if im.size == (320, 320):
        xindices = [37, 72, 103, 142, 177, 208, 247, 282]
        yindices = [21, 56, 91, 126, 161, 196, 231, 266, 301]
    elif im.size == (275, 275):
        xindices = [32, 62, 88, 122, 152, 178, 212, 242]
        yindices = [18, 48, 78, 108, 138, 168, 198, 228, 258]
    else:
        print("Image not parsed: unknown image size")
        return
    for i, x in enumerate(xindices):
        for j, y in enumerate(yindices):
            # Vertical borders
            if (i == 2 or i == 5) and c2t[rgb_im.getpixel((x, y))] == "border":
                # On thick borders, do special case
                if verbose:
                    print("Vertical border: {},{} to {},{} | {}".format(j, i, j, i + 1, c2t[rgb_im.getpixel((x + 2, y))]))
                dot_list.append((j, i, j, i + 1, c2t[rgb_im.getpixel((x, y))]))
                rgb_im.putpixel((x + 2, y), (0, 255, 0))
            elif not (i == 2 or i == 5) and (c2t[rgb_im.getpixel((x, y))] == "white" or c2t[rgb_im.getpixel((x, y))] == "black"):
                # Normal vertical border between cell j,i and cell j,i+1
                if verbose:
                    print("Vertical border: {},{} to {},{} | {} ".format(j, i, j, i + 1, c2t[rgb_im.getpixel((x, y))]))
                dot_list.append((j, i, j, i + 1, c2t[rgb_im.getpixel((x, y))]))
                rgb_im.putpixel((x, y), (0, 255, 0))
            # Horizontal borders
            if (i == 2 or i == 5) and c2t[rgb_im.getpixel((y, x))] == "border":
                # On thick borders, do special case
                if verbose:
                    print("Horizontal border: {},{} to {},{} | {}".format(i, j, i + 1, j, c2t[rgb_im.getpixel((y, x + 2))]))
                dot_list.append((i, j, i + 1, j, c2t[rgb_im.getpixel((y, x))]))
                rgb_im.putpixel((y, x + 2), (0, 255, 0))
            elif not (i == 2 or i == 5) and (c2t[rgb_im.getpixel((y, x))] == "white" or c2t[rgb_im.getpixel((y, x))] == "black"):
                # Normal horizontal border between cell j,i and cell j,i+1
                if verbose:
                    print("Horizontal border: {},{} to {},{} | {} ".format(i, j, i + 1, j, c2t[rgb_im.getpixel((y, x))]))
                dot_list.append((i, j, i + 1, j, c2t[rgb_im.getpixel((y, x))]))
                rgb_im.putpixel((y, x), (0, 255, 0))
    print("Image size: {} | Found {} dots!".format(im.size, len(dot_list)))
    if check_image:
        rgb_im.save("{}.check.gif".format(filename.split(".")[0]))
    return (filename, dot_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--download", help="Download kropki data images",
                        action="store_true")
    parser.add_argument("-p", "--parse_raw", help="Parse empty images to data format",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="More debugging output",
                        action="store_true")
    parser.add_argument("-c", "--check_image", help="Make test images to show where dots were found",
                        action="store_true")
    args = parser.parse_args()
    if args.download:
        if not os.path.exists("data"):
            os.makedirs("data")
        download_data()
    if args.parse_raw:
        codes = []
        parsed_files = 0
        for filename in os.listdir("data"):
            if "raw" in filename:
                dl = parse_raw("data/{}".format(filename), verbose=args.verbose, check_image=args.check_image)
                if dl is None:
                    continue
                codes.append(dl)
                parsed_files += 1
        print("Parsed {} files!".format(parsed_files))
        if parsed_files == 0:
            print("No files parsed, exiting..")
            exit()
        with open("parsed.json", 'w') as out:
            json.dump(codes, out)
