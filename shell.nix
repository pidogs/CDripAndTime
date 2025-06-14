let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    (pkgs.python312.withPackages (python-pkgs: [
      python-pkgs.librosa
      python-pkgs.matplotlib
      python-pkgs.numpy
      python-pkgs.pip
      python-pkgs.scipy
      python-pkgs.textual
      python-pkgs.tkinter
      python-pkgs.ttkbootstrap
    ]))
    pkgs.ffmpeg
    pkgs.vlc
    pkgs.libcdio
  ];
}
