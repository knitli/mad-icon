# Mad-Icon

## About

Mad-Icon, or simply `mad` is a cli tool that generates icons for progressive web apps (PWAs) and web applications. If you want people to be able to save your web app on their device home screen or desktop like a native app, you need to use a tool like this to generate the icons, necessary HTML, and manifest.json file. Similarly, Apple allows for web apps to have launch or launch screen images (mostly used in the app switcher to represent your app, and while loading the app). This tool generates those images as well.

### Features

- Generates icons for all platforms (Apple, Android, and Windows), up to 2025 and including *all* legacy devices and browsers.

- **Apple**: Generates icons for all iOS/iPadOS and MacOS devices, including iPhone, iPad, iPod Touch, and MacOS. WatchOS and tvOS is not currently supported; submit an issue or PR if you want to add support for that. Apple support includes:

  - Light and dark mode icons for all devices.
  - Tinted icons for all devices (not currently supported by Apple, see Apple Tinted Icons below).
  - Light and dark mode launch screen images for all devices.
  - Light and dark mode MacOS icons for the dock and desktop.

- **Android**: Generates icons for all Android devices, including legacy devices and modern devices. Android support includes:
  - Legacy icons for all devices.
  - Masked icons for all devices (Android 6.0 and above).
  - Masked monochrome icons for all devices (Android 6.0 and above).

- Generates all the necessary HTML and manifest.json files to support the icons and launch screens; uses media queries to target specific devices, platforms, and modes.

## Installation

Using pip or similar tools. For best results, use `pipx` or `uv` to install the package, which will use a virtual environment and make it available globally.

```bash
# Using pip

pip install mad-icon

# Using pipx
pipx install mad-icon

# Using uv
uv tool install mad-icon && uv tool update-shell

```

## Usage

```bash
# get the full help menu
mad --help

# Help also supports help for subcommands
mad generate-icons --help

# the generate command is a convenience command, combining generate-icons and generate-launch-screens
mad generate
```

## Tl;dr - What You Need to Get Started

### Recommended Resources

**SVG images.** you can use Inkscape[https://inkscape.org/] to modify or create them. Inkscape is free. You may also use various free and paid online tools like Figma, Canva, etc.

**Raster images.** like PNG, JPG, or WEBP, you can use any image editor like GIMP, Photoshop, etc. You can also use online tools like Canva, Figma, etc.

**Manifest/HTML.** You can use any text editor to modify the manifest.json and HTML files. You can also use online tools to modify or test your html and `manifest.json` files, such as [CodePen](https://codepen.io/) or [JSFiddle](https://jsfiddle.net/).
**Command line.** You can use any command line tool to run the mad command. You can also use online tools like [Replit](https://replit.com/) or [Glitch](https://glitch.com/) to run the command (untested).

### What You Need to Get Started

For the full package, you need:

1. **A square SVG image of your icon**. You may also use a PNG, JPG, or WEBP image, but if you do, it must be at least 1024x1024 pixels in size. This image should:

    - Be square (1:1 aspect ratio)
    - Be at least 1024x1024 pixels in size if it's not an SVG
    - Have no transparency in the background or foreground
    - Have no content within 20% of the edges of the image (for masked icons, but this provides a lowest common denominator for all icons - you can optionally supply separate files for masked vs unmasked images). Expect anything outside this area will get cropped on various devices. You can check this by taking one of your icons and drawing a centered circle over it with a radius that is 40% of one of the image's sides (a 512x512 image would have a circle with a radius of 204 pixels, or 408 pixels in diameter). If you can see any content outside the circle, it *might* get cropped on some devices.

2. **A grayscale version of your icon with *opaque*/dark background**. If you are choosing to use different images for masked vs. unmasked icons, you need a *masked* version for this (for modern android monochrome).

3. **A grayscale version of your icon with *transparent* background**. If you are choosing to use different images for masked vs. unmasked icons, you need an *unmasked* version for this (for Apple tinted icons).

4. **A color version of your icon with *transparent* background**. It should be a color version of your icon with a transparent background (for Apple dark mode).

5. **A launch Screen image OR Background Color**. You can supply either a launch screen image or a background color. If you supply a color, we will use your icon to generate launch screens for all devices, with the color as background. The plus side of this approach is that we can rotate your image to handle portrait and landscape versions. launch screen images:

    - Should be rectangular (not square)
    - if it's a raster image, at least 2868 x 2064 pixels.
    - The content should be able to be cropped to at least a 9:19.5 ratio (like 2868x1320.)

**Optional**:

- A dark mode version of your launch screen image.
- A 310x150 pixel image for the Windows 8 start menu (or 'tile').
- Separate masked and unmasked versions of your icon.

Puttit it all together, including the nice-to-haves in a directory:

```bash
mad generate \
--icon-image myicon.svg \
--masked-image my-masked-icon.svg \
--masked-image-monochrome my-masked-icon-monochrome.svg \
--darkmode-image my-darkmode-icon.svg \
--tinted-image my-tinted-icon.svg \
--tile-rectangle-image my-tile-rectangle-icon.png \
# launch screen image
--launch-screen-image my-launch-screen.svg \
--launch-darkmode-image my-launch-darkmode-screen.svg
# OR launch background color
# --colored-logo 1e061b
# You can also optionally provide a different icon file to use for the launch screen
# This is mostly for generating screens without icons with `generate-launch-screens`
# But you can use it to generate a different icon for the launch screen
# --colored-logo 1e061b my-other-icon-svg
```

### Absolute Bare Minimum (mileage may vary)

- **A square icon** (see #1 above for details)
- **A background color** (see #5 above for details)

We will try to generate everything else for you from this one image and color, but it probably won't work perfectly. You can also optionally only generate icons or launch images by using the `generate-icons` or `generate-launch-screens` commands.

Your bare-bones command would look like this:

```bash
mad generate \
--icon-image myicon.svg \
--colored-logo 1e061b
```

## Why Do I Need This? (or: Where's a Standards Body When You Need One?)

The current requirements for icons are nuanced and complicated. Taking them together, you need to provide hundreds of icons and images for your app to cover all possible cases. You can potentially use cloud image services to generate them on-the-fly, but you'll still need to provide the base images in the correct format and size and account for them in your HTML and manifest.json.

While I was developing the first version of [knitli](https://knit.li), I found that the requirements weren't well documented, and there was no tool that could handle all the modern requirements. You could piece together a solution with various tools, but it was a pain. I wanted a tool that could handle all the requirements, and I couldn't find one. So, this was born in a couple day detour from my work on knitli.

I wrote this tool to handle all the requirements for me. It generates icons for all platforms, including Apple, Android, and Windows. It also generates the necessary HTML and manifest.json files to support the icons and launch screens.
It uses media queries to target specific devices, platforms, and modes. It also generates icons for all devices, including legacy devices and modern devices. It generates icons for all platforms, including Apple, Android, and Windows. It also generates the necessary HTML and `manifest.json` markup/file to support the icons and launch screens. It uses media queries to target specific devices, platforms, and modes.

### Current Icon Requirements (April 2025)

This is based on current requirements as best I can tell. This is a moving target, and Apple's documentation is very poor in this area.

- **Apple Touch Icons**: Apple requires you define images for each icon size of all possible icon sizes, with each defined in the `<HEAD>` tag of the HTML. We consider these 'light mode' icons. Requirements:

  - In all possible resolutions (currently almost 50 sizes)
  - Fully opaque background and foreground (no transparency)
  - No rounded corners (Apple will round them for you)
  - No drop shadows (Apple will add them for you)
  - Seriously, no transparency.

- **Apple Dark Mode**: If you want your icons not to stand out in dark mode (in a bad way), you need to provide a dark mode icon. Like with the touch icons, you can use media selectors to isolate the dark mode icon (`prefers-color-scheme: dark`). You can't make this responsive -- if the user changes their preference, the icon won't change unless they revisit your app and re-add the icon.

  - In all possible resolutions (currently almost 50 sizes)
  - *transparent background* :ghost: (Apple adds a dark gradient background for you)
  - bright foreground :high-brightness:; may include a gradient. Foreground should not use transparency.
  - No rounded corners (Apple will round them for you)
  - No drop shadows (Apple will add them for you)

- **Apple Tinted Icons**: There's currently no way to specify icons for Apple's tinted icons feature. We provide tinted icons in the most likely implementation path, using `purpose='monochrome'` in the manifest.json file. These won't get used for now, but should Apple add support for tinted icons, this will probably be the way to do it.

  - *transparent background* :ghost: (Apple adds a dark gradient background for you)
  - *grayscale foreground* :gray-exclamation: (Apple adds the color tint mask for you)
  - No rounded corners (Apple will round them for you)
  - No drop shadows (Apple will add them for you)
  - No transparency in the foreground

- **Apple launch Screens**: Apple requires you define images for each icon size of all possible launch screen sizes, with each defined in the `<HEAD>` tag of the HTML. The launch screens are used in the app switcher and while loading the app. The launch screens are defined in the `manifest.json` file. You can use media queries to target light and dark modes.

  - In all possible resolutions/aspect ratios **and** orientations'
  - We allow dark mode versions using media queries if you provide a dark mode image.
  - Fully opaque background and foreground (no transparency)
  - No rounded corners (Apple will round them for you)
  - No drop shadows (Apple will add them for you)
  - Seriously, no transparency.

- **Apple MacOS Icons**: MacOS Safari, unlike all other devices, actually uses the `manifest.json` file. However, you have to supply special icons that are already cropped/masked to the rounded shape of the icon. You can define light and dark modes for the icons using the `purpose` attribute.

- **Android Legacy Icons**: For legacy Android devices, the implementation is much simpler. You just need to provide an icon image in 256x256 and 192x192 sizes. These are described in the `manifest.json` file.

- **Android Masked Icons**: Modern Android devices use masked icons, which allow manufacturers to define the shape of the icon. The specification requires you provide icons with no content (you care about) within 20% of the edges of the image, which can be cropped to fit the manufacturer shape.

- **Android Monochrome Icons**: Android also supports monochrome icons, which allow for single color icons; these need to meet the same requirements as the masked icons in terms of content.

- **Windows Icons**: Windows uses the same icons as Android, but legacy Internet Explorer and Windows 8 use special sizes, such as for the start menu. This tool generates those icons as well for the 5 people still using Windows 8 and IE 11. These are known as `tile` icons. Necessary? Probably not, but when you're already generating hundreds of icons, why not add a few more?

  - it's worth noting that there is a size that is *not square* (310x150) for the Windows 8 start (or 'tile') menu.
  - The tool allows you to specify a custom image for this rectangular icon, but will happily generate one if you don't.

## Other Useful Things

This tool includes a json file with **all** apple device resolutions, sizes, ppi, aspect ratios, and other useful information. You can generate one for yourself with `mad get-data`. We'd appreciate PRs to keep this updated when new devices get released (we'll try, but let's help each other out -- it'll be easier to maintain this than starting over).

## Contributing

We welcome contributions! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to contribute to this project.

## License

This project is licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2.0/). Tl;dr: It's a human-friendly version of the Apache 2.0 license -- you can use this code for anything you want, but we're not responsible for any problems with it, and you need to give us credit if you use/modify it.
