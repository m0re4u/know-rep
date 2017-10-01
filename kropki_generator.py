import os
import sys
import json
import re
import argparse
import urllib.request as ul
from PIL import Image


NSUDOKUS = 130


def download_data():
    for i in range(1, NSUDOKUS):
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
        (0, 0, 0): "black", (51, 51, 51): "black",
        (255, 255, 255): "white", (231, 231, 231): "white",
        (153, 153, 153): "grey", (170, 170, 170): "grey",
        (8, 8, 8): "border", (89, 89, 89): "border", (62, 62, 62): "border",
        (63, 63, 63): "border", (90, 90, 90): "border"
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
    elif im.size == (273, 273):
        xindices = [31, 61, 87, 121, 151, 177, 211, 241]
        yindices = [15, 45, 75, 105, 135, 165, 195, 225, 255]
    else:
        print("Image not parsed: unknown image size")
        return
    if verbose:
        print("File: {}".format(filename))
    for i, x in enumerate(xindices):
        for j, y in enumerate(yindices):
            if verbose:
                print("i: {}, {}x{} | {} and {}".format(i, x, y, rgb_im.getpixel((x, y)), rgb_im.getpixel((y, x))))
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
    return dot_list


def transpose_sudoku(sudoku):
    las = []
    for j in range(9):
        newl = []
        for i in range(j, 81, 9):
            newl.append(sudoku[i])
        revl = list(reversed(newl))
        las.extend(revl)
    return las


def get_solutions_from_web():
    """
    Get the solution to a sudoku from the internet
    """
    sol_dict = {}
    for i in range(1, NSUDOKUS):
        url = "https://www.janko.at/Raetsel/Sudoku-Kropki/{:03d}.a.htm".format(i)
        with ul.urlopen(url) as response:
            data = response.read()  # a `bytes` object
            ret = [x.decode("utf-8") for x in data.split()]
            a1 = ret.index("solution")
            a2 = ret.index("end")
            solution = []
            for j in range(a1 + 1, a2):
                solution.append(int(ret[j]))
        assert len(solution) == 81
        sol_dict["{:03d}".format(i)] = solution
        print("{:03d} out of {} solutions".format(i, NSUDOKUS - 1), end='\r')
    with open("solutions.json", 'w') as solution_file:
        json.dump(sol_dict, solution_file)
    print("Parsed {} solutions from the web!".format(len(sol_dict)))


def parse_solution(filename, verbose=False, check_image=False):
    """
    Uses the provided solution image to extract the solution, but is really
    unstable(current version results in ~50/NSUDOKUS solutions)
    """
    import pytesseract

    exclude_transpose = ["001"]
    res = pytesseract.image_to_string(Image.open(filename))
    print(filename)
    su = ""
    for line in res.split("\n"):
        match = re.findall('^[a-zAC-Z\.0]+', line)
        if match:
            continue
        corr1 = re.sub("no|B", "8", line)
        corr2 = re.sub("844", "8 4", corr1)
        corr2 = re.sub("[a-zA-Z0.&`’~\-]", " ", corr2)

        match = re.findall('\s', line)
        if not match:
            corr2 = " ".join([x for x in corr2])
        if re.findall('[0-9]+', corr2):
            su += corr2 + " "
    try:
        solution = [int(x) for x in su.split()]
    except Exception as e:
        return
    if len(solution) != 81 and len(solution) != 0:
        # print(res)
        # print("Incorrect total number of digits")
        # print("Solution({}): {}".format(len(solution), solution))
        return
    elif len(solution) == 0:
        # print("No numbers recognized!")
        return
    if re.findall("\d+", filename)[0] not in exclude_transpose:
        solution = transpose_sudoku(solution)
    ex = 0
    for i in range(1, 10):
        if solution.count(i) != 9:
            # print("Not nine digits {}!".format(i))
            ex = 1
    if ex == 1:
        # print(res)
        return
    # print(solution)
    return solution


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Create a dataset of kropki sudoku's to use in \
                     testing a solver.")
    parser.add_argument("-d", "--download", help="Download kropki data images",
                        action="store_true")
    parser.add_argument("-p", "--parse_raw", help="Parse empty images to data format",
                        action="store_true")
    parser.add_argument("-s", "--parse_solution", help="Parse solution images to data format",
                        action="store_true")
    parser.add_argument("-w", "--web_solution", help="Retrieve the solution from the web",
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
        codes = {}
        parsed_files = 0
        for filename in os.listdir("data"):
            if "raw" in filename:
                dl = parse_raw("data/{}".format(filename), verbose=args.verbose, check_image=args.check_image)
                if dl is None:
                    continue
                codes[filename] = dl
                parsed_files += 1
        print("Parsed {} empty files!".format(parsed_files))
        if parsed_files != 0:
            with open("parsed.json", 'w') as out:
                json.dump(codes, out)
    if args.parse_solution:
        print("[!!!] WARNING [!!!]: unstable solution provider")
        sols = {}
        parsed_files = 0
        for filename in os.listdir("data"):
            if "solution" in filename:
                exclude = ["003"]
                if re.findall("\d+", filename)[0] in exclude:
                    continue

                sol = parse_solution("data/{}".format(filename), verbose=args.verbose, check_image=args.check_image)
                if sol is None:
                    print("Skipping {}".format(filename))
                    continue
                sols[filename] = sol
                parsed_files += 1
        print("Parsed {} solution files!".format(parsed_files))
        if parsed_files != 0:
            with open("solutions.json", 'w') as out:
                json.dump(sols, out)
    if args.web_solution:
        get_solutions_from_web()
