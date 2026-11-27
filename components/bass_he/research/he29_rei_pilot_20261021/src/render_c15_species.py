"""Reproduce the accepted sparse-tick C15 species plot from derived data.

Run: MPLCONFIGDIR=/tmp/he29_mpl python src/render_c15_species.py
This plotting entry point performs no integration and does not rewrite tables.
"""
from species_stress import render_c15_saved
if __name__=='__main__':render_c15_saved()
