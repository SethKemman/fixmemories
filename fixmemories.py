import os
from PIL import Image
from colorama import Fore, Back, Style
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip
import shutil

memories = "memories"


def get_overlays():
    overlays = []
    for file in os.listdir(memories):
        if file.endswith("-overlay.png"):
            overlays.append(file)
    return overlays

def get_main_images():
    main_images = []
    for file in os.listdir(memories):
        if file.endswith("-main.jpg"):
            main_images.append(file)
    return main_images

def get_main_videos():
    main_videos = []
    for file in os.listdir(memories):
        if file.endswith("-main.mp4"):
            main_videos.append(file)
    return main_videos

def get_image_matches():
    matches = []
    for file in get_main_images():
        mainfile = file.split("-main.jpg")[0]
        for overlayfile in get_overlays():
            if overlayfile.startswith(mainfile) and overlayfile.endswith("-overlay.png"):
                matches.append((file, overlayfile))
    return matches

def get_image_match(filename):
    mainfile = filename.split("-main.jpg")[0]
    for overlayfile in get_overlays():
        if overlayfile.startswith(mainfile) and overlayfile.endswith("-overlay.png"):
            return (filename, overlayfile)
    return None


def get_video_matches():
    matches = []
    for file in get_main_videos():
        mainfile = file.split("-main.mp4")[0]
        for overlayfile in get_overlays():
            if overlayfile.startswith(mainfile) and overlayfile.endswith("-overlay.png"):
                matches.append((file, overlayfile))
    return matches

def get_video_match(filename):
    mainfile = filename.split("-main.mp4")[0]
    for overlayfile in get_overlays():
        if overlayfile.startswith(mainfile) and overlayfile.endswith("-overlay.png"):
            return (filename, overlayfile)
    return None

def complete_image_match(mainfile):
    filename = mainfile
    match = get_image_match(mainfile)
    if match:
        # Do something with the matched files, e.g., overlay the image
        mainfile = "memories/" + match[0]
        overlayfile = "memories/" + match[1]

        backgroundimage = Image.open(mainfile)
        overlayimage = Image.open(overlayfile)

        backgroundimage.paste(overlayimage, overlayimage)

        backgroundimage = backgroundimage.convert('RGB')

        backgroundimage.save(f"fixedImages/{filename}")

def complete_video_match(mainfile):
    match = get_video_match(mainfile)
    filename = mainfile
    if match:
        mainfile = "memories/" + match[0]
        overlayfile = "memories/" + match[1]

        print(mainfile)
        print(overlayfile)

        # 1. Load background video
        backgroundvideo = VideoFileClip(mainfile)
        print("backgroundimage")

        # 2. Load overlay image, set duration, and ensure it matches the background dimensions
        overlayimage = (
            ImageClip(overlayfile)
            .resized(backgroundvideo.size)
            .with_duration(backgroundvideo.duration)
            .with_position((0, 0))
        )
        print("overlay thing")

        # 3. Composite with explicit duration set on the final clip
        final_video = (
            CompositeVideoClip([backgroundvideo, overlayimage])
            .with_duration(backgroundvideo.duration)
        )
        print("comp")

        # 4. Export final video
        mainfile_base = mainfile.split("-main.mp4")[0]
        final_video.write_videofile(
            f"{mainfile_base}_output.mp4",
            fps=backgroundvideo.fps or 24,
        )

        final_video.write_videofile(f"fixedVideos/{filename}")

        # Clean up open file handles
        backgroundvideo.close()
        overlayimage.close()
        final_video.close()

    
def get_stats():
    print(Fore.WHITE + f"{len(get_overlays())} overlays found")
    print(Fore.WHITE + f"{len(get_main_images())} main images found")
    print(Fore.WHITE + f"{len(get_main_videos())} main videos found")
    print(Fore.GREEN + f"{len(get_image_matches())} image matches found")
    print(Fore.GREEN + f"{len(get_video_matches())} video matches found")
    print(Style.RESET_ALL)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    get_stats()

    fiximages = input("Fix all images (y/n): ")
    if fiximages.lower() == "y":
        index = 0
        if os.path.isdir("fixedImages") == False:
            os.mkdir("fixedImages")
        for image in get_main_images():
            os.system('cls' if os.name == 'nt' else 'clear')
            if get_image_match(image) != None:
                complete_image_match(image)
            else:
                try:
                    shutil.copy(f"{memories}/{image}", "fixedImages")

                except shutil.SameFileError:
                    print("Source and destination represents the same file.")

                except PermissionError:
                    print("Permission denied.")

                except:
                    print("Error occurred while copying file.")

            print(f"Fixed {index} out of {len(get_main_images())} ")
            index += 1
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + f"Fixed {index} from the {len(get_main_images())} images.")
        print(Style.RESET_ALL + Fore.RESET)
        zipimages = input("Zip image folder (y/n): ")
        if zipimages.lower() == "y":
            shutil.make_archive("imagesZipped", 'zip', "fixedImages")

    fixvideos = input("Fix all videos (y/n): ")
    if fixvideos.lower() == "y":
        if os.path.isdir("fixedVideos") == False:
            os.mkdir("fixedVideos")
        for match in get_video_matches():
            complete_video_match(match[0])
        zipvideos = input("Zip video folder (y/n): ")
        if zipvideos.lower() == "y":
            shutil.make_archive("videosZipped", 'zip', "fixedVideos")
    else:
        os.system('cls')
        input("Done")


main()