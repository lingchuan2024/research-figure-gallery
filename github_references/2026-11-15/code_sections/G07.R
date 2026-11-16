# G07: upstream example code excerpt — not executed locally.
# Source: https://github.com/krassowski/complex-upset/blob/79fa000ca4087d55ee2d8cf1a0fb7a01bb5aba7e/README.md
# Local snapshot: candidates_efficiency/complex_upset_README.md
# Extraction: Showcase R fenced block, lines 21–57
# Adaptations: only this provenance/license header added; original dependency-install statement retained but never run here
# This file is provided for offline reading; no original-image reproduction is claimed.
#
# Upstream license retained below:
# MIT License
#
# Copyright (c) 2020 Michał Krassowski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Offline use requires all packages below already installed.
# The upstream if(!require(...)) install.packages(...) line is retained verbatim.
library(ggplot2)
library(ComplexUpset)

if(!require(ggplot2movies)) install.packages('ggplot2movies')
movies = ggplot2movies::movies
genres = c('Action', 'Animation', 'Comedy', 'Drama', 'Documentary', 'Romance')

upset(
    movies,
    genres,
    annotations = list(
        'Length'=ggplot(mapping=aes(x=intersection, y=length)) + geom_boxplot(),
        'Rating'=ggplot(mapping=aes(x=intersection, y=rating))
            # if you do not want to install ggbeeswarm, you can use geom_jitter
            + ggbeeswarm::geom_quasirandom(aes(color=log10(votes)))
            + geom_violin(width=1.1, alpha=0.5)
    ),
    queries=list(
        upset_query(
            intersect=c('Drama', 'Comedy'),
            color='red',
            fill='red',
            only_components=c('intersections_matrix', 'Intersection size')
        ),
        upset_query(
            set='Drama',
            fill='blue'
        ),
        upset_query(
            intersect=c('Romance', 'Drama'),
            fill='yellow',
            only_components=c('Length')
        )
    ),
    min_size=10,
    width_ratio=0.1
)
