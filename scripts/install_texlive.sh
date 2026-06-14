#!/bin/bash
set -e
cd /tmp
wget -q https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
tar -xzf install-tl-unx.tar.gz
cd install-tl-*/

cat > /tmp/texlive.profile << 'PROFILE'
selected_scheme scheme-small
TEXDIR /workspace/texlive
TEXMFLOCAL /workspace/texlive/texmf-local
TEXMFSYSCONFIG /workspace/texlive/texmf-config
TEXMFSYSVAR /workspace/texlive/texmf-var
TEXMFCONFIG ~/.texlive/texmf-config
TEXMFVAR ~/.texlive/texmf-var
TEXMFHOME ~/texmf
option_doc 0
option_src 0
PROFILE

./install-tl --profile=/tmp/texlive.profile

# Add to PATH permanently in /workspace
echo 'export PATH="/workspace/texlive/bin/x86_64-linux:$PATH"' >> /root/.bashrc

# Install packages needed for MDT template
export PATH="/workspace/texlive/bin/x86_64-linux:$PATH"
tlmgr install biber biblatex koma-script acronym csquotes siunitx pdfpages \
    collection-fontsrecommended babel-german hyphen-german

echo "TeX Live installation complete!"
