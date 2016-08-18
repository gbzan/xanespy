# -*- coding: utf-8 -*-
#
# Copyright © 2016 Mark Wolf
#
# This file is part of Xanespy.
#
# Xanespy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Xanespy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Xanespy. If not, see <http://www.gnu.org/licenses/>.

import gc
import warnings

from matplotlib import figure, pyplot, cm, animation
from matplotlib.gridspec import GridSpec
from matplotlib.cm import get_cmap
from matplotlib.colors import BoundaryNorm, Normalize
import numpy as np
# May not import if not installed
try:
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
except (TypeError, ImportError):
    pass

from utilities import component
import exceptions
import plots
from animation import FrameAnimation


# class FramesetPlotter():
#     """A class that handles the graphic display of TXM data. It should be
#     thought of as an interface to a plotting library, such as
#     matplotlib.
#     """
#     map_cmap = "plasma"
#     active_representation = "modulus" # Default will be used unless changed

#     def __init__(self, frameset, map_ax=None, goodness_ax=None, im_ax=None):
#         self.map_ax = map_ax
#         if im_ax is None:
#             self.im_ax = plots.new_image_axes()
#         else:
#             self.im_ax = im_ax
#         self.goodness_ax = goodness_ax
#         self.frameset = frameset

#     def draw_colorbar(self, norm_range=None):
#         """Add colormap to the side of the axes."""
#         norm = self.map_normalizer(norm_range=norm_range)
#         edge = self.frameset.edge()
#         energies = edge.energies_in_range(norm_range=norm_range)
#         mappable = cm.ScalarMappable(norm=norm, cmap=self.map_cmap)
#         mappable.set_array(np.arange(0, 3))
#         self.cbar = pyplot.colorbar(mappable,
#                                     ax=self.map_ax,
#                                     ticks=energies[0:-1],
#                                     spacing="proportional")
#         self.cbar.ax.xaxis.get_major_formatter().set_useOffset(False)
#         self.cbar.ax.set_title('eV')

#     def map_normalizer(self, norm_range=None):
#         cmap = cm.get_cmap(self.map_cmap)
#         norm = self.frameset.edge().map_normalizer()
#         # norm = self.frameset.edge().map_normalizer(method=self.frameset.map_method)
#         # edge = self.frameset.edge()
#         # energies = edge.energies_in_range(norm_range=norm_range)
#         # if self.frameset.map_method == "direct":
#         #     # Discrete normalization range
#         #     norm = BoundaryNorm(energies, cmap.N)
#         # else:
#         #     # Continuous normalization range
#         #     norm = Normalize(energies[0], energies[-1])
#         return norm

#     def draw_map(self, norm_range=None, alpha=1,
#                  goodness_filter=False, *args, **kwargs):
#         """Draw a map on the map_ax. If no axes exist, a new Axes is created
#         with a colorbar."""
#         # Construct a discrete normalizer so the colorbar is also discrete
#         norm = self.map_normalizer(norm_range=norm_range)
#         # Create a new axes if necessary
#         if self.map_ax is None:
#             self.map_ax = plots.new_image_axes()
#             self.draw_colorbar()  # norm=norm, ticks=energies[0:-1])
#         # Plot chemical map (on top of absorbance image, if present)
#         extent = self.frameset.extent()
#         masked_map = self.frameset.masked_map(goodness_filter=goodness_filter)
#         artist = self.map_ax.imshow(np.abs(masked_map),
#                                     extent=extent,
#                                     cmap=self.map_cmap,
#                                     origin="lower",
#                                     norm=norm,
#                                     alpha=alpha,
#                                     *args, **kwargs)
#         # Decorate axes labels, etc
#         self.map_ax.set_xlabel(self.frameset[0].pixel_size.unit)
#         self.map_ax.set_ylabel(self.frameset[0].pixel_size.unit)
#         return artist

#     def draw_goodness(self, norm_range=None, alpha=1, *args, **kwargs):
#         """Draw a map of the goodness of fit on the map_ax. If no axes exist,
#         a new Axes is created with a colorbar.
#         """
#         # Create a new axes if necessary
#         if self.goodness_ax is None:
#             self.goodness_ax = plots.new_image_axes()
#         # Plot chemical map (on top of absorbance image, if present)
#         extent = self.frameset.extent()
#         goodness_map = self.frameset.goodness_filter()
#         artist = self.goodness_ax.imshow(component(goodness_map, "modulus"),
#                                          extent=extent,
#                                          cmap=self.map_cmap,
#                                          origin="lower",
#                                          alpha=alpha,
#                                          *args, **kwargs)
#         # Decorate axes labels, etc
#         self.goodness_ax.set_xlabel("µm")
#         self.goodness_ax.set_ylabel("µm")
#         return artist

#     def plot_histogram(self, ax=None, norm_range=None, goodness_filter=False, representation="modulus"):
#         if ax is None:
#             ax = plots.new_axes()
#         # Set normalizer
#         if norm_range is None:
#             norm_range = self.frameset.edge.map_range
#         norm = Normalize(norm_range[0], norm_range[1])
#         masked_map = self.frameset.masked_map(goodness_filter=goodness_filter)
#         mask = masked_map.mask
#         # Add a bin for any above and below the range
#         edge = self.frameset.edge()
#         # energies = self.frameset.edge().energies_in_range(norm_range=norm_range)
#         # energies = [
#         #     2 * energies[0] - energies[1],
#         #     *energies,
#         #     2 * energies[-1] - energies[-2]
#         # ]
#         clipped_map =  np.clip(masked_map, edge.map_range[0], edge.map_range[1])
#         n, bins, patches = ax.hist(component(clipped_map[~mask], name="modulus").flatten(),
#                                    bins=100)
#         # Set colors on histogram
#         for patch in patches:
#             x_position = patch.get_x()
#             cmap = get_cmap(self.map_cmap)
#             color = cmap(norm(x_position))
#             patch.set_color(color)
#         # Set axes decorations
#         ax.set_xlabel("Whiteline position /eV")
#         ax.set_ylabel("Pixels")
#         ax.set_xlim(edge.map_range[0], edge.map_range[1])
#         # ax.xaxis.set_ticks(energies)
#         ax.xaxis.get_major_formatter().set_useOffset(False)
#         return ax

#     def draw_crosshairs(self, active_xy=None, color="black", ax=None):
#         # Remove old cross-hairs
#         if getattr(self, 'map_crosshairs', None):
#             for line in self.map_crosshairs:
#                 line.remove()
#             self.map_crosshairs = None
#         # Draw cross-hairs on the map if there's an active pixel
#         if active_xy:
#             xline = self.map_ax.axvline(x=active_xy.x,
#                                         color=color, linestyle="--")
#             yline = self.map_ax.axhline(y=active_xy.y,
#                                         color=color, linestyle="--")
#             self.map_crosshairs = (xline, yline)
#         self.map_ax.figure.canvas.draw()


# class FramesetMoviePlotter(FramesetPlotter):
#     show_particles = False

#     def create_axes(self, figsize=(13.8, 6)):
#         self.figure = figure.Figure(figsize=figsize)
#         self.figure.subplots_adjust(bottom=0.2)
#         self.canvas = FigureCanvasGTK3Agg(figure=self.figure)
#         # self.canvas = FigureCanvasGTK3Agg(figure=self.figure)
#         # Create figure grid layout
#         self.image_ax = self.figure.add_subplot(1, 2, 1)
#         plots.set_outside_ticks(self.image_ax)
#         plots.remove_extra_spines(ax=self.image_ax)
#         self.xanes_ax = self.figure.add_subplot(1, 2, 2)
#         plots.remove_extra_spines(ax=self.xanes_ax)
#         return (self.image_ax, self.xanes_ax)

#     def connect_animation(self, interval=50, repeat=True, repeat_delay=3000):
#         # Draw the non-animated parts of the graphs
#         self.plot_xanes_spectrum()
#         # Create artists
#         all_artists = []
#         for frame in self.frameset:
#             frame_artist = frame.plot_image(ax=self.image_ax,
#                                             show_particles=False,
#                                             norm=self.frameset.image_normalizer(),
#                                             animated=True)
#             # Get Xanes highlight artists
#             energy = frame.energy
#             intensity = self.frameset.xanes_spectrum()[energy]
#             xanes_artists = self.xanes_ax.plot([energy], [intensity], 'ro',
#                                                animated=True)
#             # xanes_artists.append(xanes_artist[0])
#             if self.show_particles:
#                 # Get particle labels artists
#                 particle_artists = frame.plot_particle_labels(
#                     ax=self.image_ax,
#                     extent=frame.extent(),
#                     animated=True
#                 )
#             else:
#                 particle_artists = []
#             #all_artists.append((frame_artist, *xanes_artists, *particle_artists))
#             # all_artists.append((frame_artist,))
#         # Prepare animation
#         self.frame_animation = animation.ArtistAnimation(fig=self.figure,
#                                                          artists=all_artists,
#                                                          interval=interval,
#                                                          repeat=repeat,
#                                                          repeat_delay=repeat_delay,
#                                                          blit=True)

#     def show(self):
#         self.figure.canvas.show()

#     def save_movie(self, *args, **kwargs):
#         # Set default values
#         kwargs['codec'] = kwargs.get('codec', 'h264')
#         kwargs['bitrate'] = kwargs.get('bitrate', -1)
#         kwargs['writer'] = 'ffmpeg'
#         self.figure.canvas.draw()
#         return self.frame_animation.save(*args, **kwargs)


class GtkFramesetPlotter():
    """A class that handles the graphic display of TXM data using GTK
    canvases, keeping track of things like active representation and
    axes for each plot type. It should be thought of as an interface
    to a plotting library, such as matplotlib.
    """
    map_cmap = "plasma"
    show_particles = False
    xanes_scatter = None
    map_crosshairs = None
    image_crosshairs = None
    apply_edge_jump = False
    active_xy = None
    active_pixel = None
    normalize_xanes = True
    normalize_map_xanes = True
    active_representation = "absorbances"

    def __init__(self, frameset):
        self.frameset = frameset
        # To preserve previous plots
        pyplot.figure()
        # Figures for drawing images of frames
        self._frame_fig = figure.Figure(figsize=(13.8, 10))
        self.frame_canvas = FigureCanvasGTK3Agg(self._frame_fig)
        self.frame_canvas.set_size_request(400, 400)
        # Figures for overall chemical map
        self._map_fig = figure.Figure(figsize=(13.8, 10))
        self.map_canvas = FigureCanvasGTK3Agg(self._map_fig)
        self.map_canvas.set_size_request(400, 400)

    def draw_map(self, show_map=True,
                 show_background=False):
        # Clear old mapping data
        self.map_ax.clear()
        self.map_crosshairs = None
        artists = []
        # Show or hide maps as dictated by GUI toggle buttons
        if show_background:
            # Plot the absorbance background image
            bg_artist = self.frameset.plot_mean_image(ax=self.map_ax)
            bg_artist.set_cmap('gray')
            artists.append(bg_artist)
            map_alpha = 0.4
        else:
            map_alpha = 1
        if show_map:
            with self.frameset.store() as store:
                data = store.whiteline_map.value
            if self.apply_edge_jump:
                data = np.ma.array(data, mask=self.frameset.edge_mask())
            # Plot the overall map
            extent = self.frameset.extent(representation=self.active_representation)
            artist = plots.plot_txm_map(data,
                                        edge=self.frameset.edge(),
                                        ax=self.map_ax,
                                        norm=None,
                                        extent=extent)
            # artist = self.frameset.plot_map(goodness_filter=self.apply_edge_jump,
            #                                 alpha=map_alpha)
            # map_artist = super().draw_map(goodness_filter=self.apply_edge_jump,
            #                               alpha=map_alpha)
            artists.append(artist)
        # Force redraw
        self.map_canvas.draw()
        return artists

    def plot_histogram(self):
        # Get data
        with self.frameset.store() as store:
            data = store.whiteline_map.value
        if self.apply_edge_jump:
            data = np.ma.array(data, mask=self.frameset.edge_mask())
        # Plot histogram
        plots.plot_txm_histogram(data=data, ax=self.map_hist_ax, cmap=self.map_cmap)

    def draw_crosshairs(self, active_xy=None, color="black"):
        # Remove old cross-hairs
        if getattr(self, 'map_crosshairs', None):
            for line in self.map_crosshairs:
                line.remove()
            self.map_crosshairs = None
        # Draw cross-hairs on the map if there's an active pixel
        if active_xy:
            xline = self.map_ax.axvline(x=active_xy.x,
                                        color=color, linestyle="--")
            yline = self.map_ax.axhline(y=active_xy.y,
                                        color=color, linestyle="--")
            self.map_crosshairs = (xline, yline)
        self.map_ax.figure.canvas.draw()
        self.image_ax.figure.canvas.draw()

    def draw_map_xanes(self, active_pixel=None):
        raise UserWarning("Just call draw_xanes_spectra")

    def _plot_spectrum(self, ax, active_pixel=None, zoom=True):
        """Get the data and plot on the given ax"""
        show_fit = False
        # Decide whether to apply edge jump filter
        if self.active_pixel:
            edge_jump = False
        else:
            edge_jump = self.apply_edge_jump
        spectrum = self.frameset.spectrum(edge_jump_filter=edge_jump, pixel=active_pixel)
        norm = Normalize(*self.frameset.edge.map_range)
        # Plot the full XANES spectrum
        ax.clear()
        plots.plot_xanes_spectrum(spectrum=spectrum,
                                  energies=spectrum.index,
                                  norm=norm,
                                  ax=ax)

    def plot_map_spectra(self, active_pixel=None):
        """Plot the XANES spectra on the axes in the map window."""
        self._plot_spectrum(ax=self.map_xanes_ax, active_pixel=active_pixel)
        self._plot_spectrum(ax=self.map_edge_ax, active_pixel=active_pixel)
        # Zoom in on the edge axis
        map_range = self.frameset.edge.map_range
        self.map_edge_ax.set_xlim(map_range[0]-5, map_range[1]+5)
        self.map_canvas.draw()

    def plot_frame_spectra(self, active_pixel=None):
        """Plot the XANES spectra on the axes in the frame window."""
        self._plot_spectrum(ax=self.xanes_ax, active_pixel=active_pixel)
        self._plot_spectrum(ax=self.edge_ax, active_pixel=active_pixel)
        # Zoom in on the edge axis
        map_range = self.frameset.edge.map_range
        self.edge_ax.set_xlim(map_range[0]-5, map_range[1]+5)
        self.frame_canvas.draw()
        # plots.plot_xanes_spectrum(spectrum=spectrum,
        #                           energies=spectrum.index,
        #                           norm=norm,
        #                           ax=self.map_xanes_ax)
        # plots.plot_xanes_spectrum(spectrum=spectrum,
        #                           energies=spectrum.index,
        #                           norm=norm,
        #                           ax=self.xanes_ax)
        # # Plot the XANES spectrum zoomed in on the edge
        # self.map_edge_ax.clear()
        # self.edge_ax.clear()
        # plots.plot_xanes_spectrum(spectrum=spectrum,
        #                           energies=spectrum.index,
        #                           norm=norm,
        #                           ax=self.map_edge_ax)
        # plots.plot_xanes_spectrum(spectrum=spectrum,
        #                           energies=spectrum.index,
        #                           norm=norm,
        #                           ax=self.edge_ax)
        # map_range = self.frameset.edge.map_range
        # self.map_edge_ax.set_xlim(map_range[0]-5, map_range[1]+5)
        # self.edge_ax.set_xlim(map_range[0]-5, map_range[1]+5)

    def plot_xanes_spectra(self, *args, **kwargs):
        raise UserWarning("Calling plot_map_spectra instead")
        return self.plot_map_spectra(*args, **kwargs)

    def create_axes(self):
        # Define a grid specification
        gridspec = GridSpec(2, 2)
        # Create figure grid layout
        image_spec = gridspec.new_subplotspec((0, 0), rowspan=2)
        self.image_ax = self.frame_figure.add_subplot(image_spec)
        plots.set_outside_ticks(self.image_ax)
        plots.remove_extra_spines(self.image_ax)
        xanes_spec = gridspec.new_subplotspec((0, 1))
        self.xanes_ax = self.frame_figure.add_subplot(xanes_spec)
        plots.remove_extra_spines(self.xanes_ax)
        edge_spec = gridspec.new_subplotspec((1, 1))
        self.edge_ax = self.frame_figure.add_subplot(edge_spec)
        plots.remove_extra_spines(self.edge_ax)

        # Create mapping axes
        map_spec = gridspec.new_subplotspec((0, 0), rowspan=2)
        self.map_ax = self.map_figure.add_subplot(map_spec)
        plots.set_outside_ticks(self.map_ax)
        xanes_spec = gridspec.new_subplotspec((0, 1), colspan=2)
        self.map_xanes_ax = self.map_figure.add_subplot(xanes_spec)
        self.map_hist_ax = self.map_figure.add_subplot(2, 4, 7)
        self.map_edge_ax = self.map_figure.add_subplot(2, 4, 8)

    def draw(self):
        self.frame_figure.canvas.draw()
        self.image_ax.figure.canvas.draw()
        self.xanes_ax.figure.canvas.draw()

    @property
    def frame_figure(self):
        return self._frame_fig

    @property
    def map_figure(self):
        return self._map_fig

    def refresh_artists(self):
        """Prepare artist objects for each frame and animate them for easy
        transitioning."""
        self.plot_frame_spectra(active_pixel=self.active_pixel)
        # Get image artists
        self.image_ax.clear()
        # Prepare appropriate xanes spectrum
        spectrum = self.frameset.spectrum(edge_jump_filter=self.apply_edge_jump,
                                          pixel=self.active_pixel)
        # if self.normalize_xanes:
            # edge = self.frameset.edge()
            # edge.post_edge_order = 1
            # try:
            #     edge.fit(spectrum)
            #     spectrum = edge.normalize(spectrum)
            # except exceptions.RefinementError:
            #     pass
        # Prepare individual frame artists
        frame_artists = []
        with self.frameset.store() as store:
            extent = self.frameset.extent(self.active_representation)
            frames = store.get_frames(name=self.active_representation)
            self.norm = Normalize(np.min(frames),
                                  np.max(frames))
            for img in frames.value:
                artist = self.image_ax.imshow(img, origin='lower',
                                              animated=True, cmap="gray",
                                              extent=extent,
                                              norm=self.norm)
                artist.set_visible(False)
                frame_artists.append(artist)
        # Prepare XANES highlighting artists
        xanes_artists = []
        spectrum = self.frameset.spectrum(edge_jump_filter=self.apply_edge_jump)
        for energy in spectrum.index:
            artists = self.xanes_ax.plot([energy], [spectrum[energy]],
                                         'ro', animated=True)
            artists += self.edge_ax.plot([energy], [spectrum[energy]],
                                         'ro', animated=True)
            [a.set_visible(False) for a in artists]
            xanes_artists.append(artists)
        #     if self.show_particles:
        #         # Get particle labels artists
        #         particle_artists = frame.plot_particle_labels(
        #             ax=self.image_ax,
        #             extent=frame.extent(),
        #             animated=True
        #         )
        #         [a.set_visible(False) for a in particle_artists]
        #     else:
        #         particle_artists = []
        #             # Draw cross-hairs on the map if there's an active pixel
        #     if self.active_xy:
        #         # Draw cross-hairs on the image axes
        #         xline = self.image_ax.axvline(x=self.active_xy.x,
        #                                       color='red', linestyle="--",
        #                                       animated=True, zorder=10)
        #         yline = self.image_ax.axhline(y=self.active_xy.y,
        #                                       color='red', linestyle="--",
        #                                       animated=True, zorder=10)
        #         crosshairs = [xline, yline]
        #     else:
        #         crosshairs = []
                # all_artists.append((frame_artist, *xanes_artists,
                #                     *particle_artists, *crosshairs))
        # Combined into a 2-D list of artists
        all_artists = []
        for frm, xas in zip(frame_artists, xanes_artists):
            all_artists.append((frm, *xas,))
        # Add artists to the animation object
        self.frame_animation.artists = all_artists
        self.frame_canvas.draw()
        return all_artists

    def connect_animation(self, event_source):
        if hasattr(self, 'frame_animation'):
            # Disconnect old animation
            self.frame_animation.stop()
        self.frame_animation = FrameAnimation(fig=self.frame_figure,
                                              artists=[],
                                              event_source=event_source,
                                              blit=True)
        self.refresh_artists()
        # Forces the animation to show the first frame
        # event_source._on_change()
        self.frame_canvas.draw()

    def destroy(self):
        """Remove figures and attempt to reclaim memory."""
        # Delete animation
        if hasattr(self, 'frame_animation'):
            self.frame_animation.stop()
            del self.frame_animation
        # Clear axes and figures
        self.image_ax.clear()
        self.image_ax.figure.clf()
        pyplot.close(self.image_ax.figure)
        if hasattr(self, 'map_ax'):
            self.map_ax.clear()
            self.map_ax.figure.clf()
            pyplot.close(self.map_ax.figure)
        gc.collect()


class DummyGtkPlotter(GtkFramesetPlotter):
    def connect_animation(self, *args, **kwargs):
        pass