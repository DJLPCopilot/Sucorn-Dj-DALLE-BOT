def main():
    """cli tool that launches a labelling program, labels only files with a placeholder "xxxxxxxx"
    Press 0 for negative, 1 for positive and 2 for unsure
    Required positional argument: folder-name
    --rewrite: adds already labeled images to the labeller, will overwrite the old label"""
    parser = argparse.ArgumentParser(description='Image Labeling Program')
    parser.add_argument('folder_name', type=str, help='Folder name of images')
    parser.add_argument('--rewrite', action='store_true', help='Rewrite all images regardlesss of label')
    parser.add_argument('--reset', action='store_true', help='Reset images')
    parser.add_argument('-c', '--category', choices=['positive', 'negative', 'neutral'], help='Label images with the following category')

    args = parser.parse_args()
    options = {"rewrite": args.rewrite, "category": args.category}

    folder_path = f"{os.path.dirname(os.path.realpath(__file__))}/../images/{args.folder_name}"
    if not os.path.isdir(folder_path):
        print(f'Directory not found: {folder_path}')
        return
    else:
        for subfolder in ['positive', 'neutral', 'negative']:
            subfolder_path = os.path.join(folder_path, subfolder)
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)
                print(f"Created folder as it does not exist: {subfolder_path}") 

    if args.reset: # TODO: Update for new structure
        confirmation = input(f"Are you sure you wish to reset the labels of the following directory? {args.folder_name} (N) ")
        if confirmation.lower() != "y":
            print("Quitting")
        else:
            for current_file in [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg')]:
                base_name, extension = os.path.splitext(current_file)
                for replacements in ["_Positive", "_Negative", "_positive", "_negative"]:
                    base_name = base_name.replace(replacements, "")
                new_filename = base_name + extension
                os.rename(os.path.join(folder_path, current_file), os.path.join(folder_path, new_filename))
            print("Reset")
        return

    image_labeler = ImageLabeler(folder_path=folder_path, options=options)
    image_labeler.show_image()
    image_labeler.root.mainloop()

if __name__ == "__main__":
    main()