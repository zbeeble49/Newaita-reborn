<div align="center">
    <img src="icon.png" width="200" height="200" />
    <h1>Newaita reborn</h1>
    <p>Remaster Newaita icon theme. Refreshed and made cleaner.</p>
    <img src="cover.png" />
</div>

## Variants

| Variant | Folder color |
|---|---|
| `Newaita-reborn` / `-dark` | blue (standard) |
| `Newaita-reborn-chameleon` / `-chameleon-dark` | **follows the Plasma accent / highlight color** |
| `Newaita-reborn-black` / `-black-dark` | black |
| `Newaita-reborn-brown` / `-brown-dark` | brown |
| `Newaita-reborn-gray` / `-gray-dark` | gray |
| `Newaita-reborn-green` / `-green-dark` | green |
| `Newaita-reborn-lime` / `-lime-dark` | lime |
| `Newaita-reborn-orange` / `-orange-dark` | orange |
| `Newaita-reborn-pink` / `-pink-dark` | pink |
| `Newaita-reborn-purple` / `-purple-dark` | purple |
| `Newaita-reborn-red` / `-red-dark` | red |
| `Newaita-reborn-teal` / `-teal-dark` | teal |
| `Newaita-reborn-yellow` / `-yellow-dark` | yellow |

### Chameleon

The chameleon variants draw their folders with KDE's `ColorScheme-Highlight`
stylesheet class, so Plasma (KIconLoader) paints them in the current accent /
selection color of your color scheme – change the accent color in
*System Settings → Colors & Themes → Colors* and the folders follow.
Outside of KDE applications (e.g. GTK apps) the folders fall back to Breeze blue.

### Rebuilding the variants

All color variants are generated from `Newaita-reborn` and `Newaita-reborn-dark`
and the `places/48/folder-<color>.svg` templates:

```shell
tools/build-variants.py --clean
```

## Installation

After downloading and extracting, move the `Newaita-reborn` and `Newaita-reborn-dark` folders **plus** any variant folders you want (variants symlink into the two base themes) to:
- `/usr/share/icons` if you want them to be visible for all users.
- `~/.icons` on **GTK** or `~/.local/share/icons` on **KDE** if you want them to be visible only to your user.

### For Arch Linux users

```shell
# With Yay or another AUR helper of your choice
yay -S newaita-reborn-icons-git
```

Thanks to [Cahian Freire](https://github.com/cahian)

## Support

Even a small donation boosts motivation :)


[![Юmoney](https://i.imgur.com/KrkyEbB.png)](https://yoomoney.ru/to/41001796418567)
