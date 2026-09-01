/* Rolling gallery: continuous marquee with press-and-hold dragging.
   Progressive enhancement -- without JS the CSS animation still runs.
   The track holds its image list exactly twice, so wrapping the offset by one
   half-width keeps the loop seamless in both directions. */
(function () {
	'use strict';

	var reduceMotion = window.matchMedia
		&& window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	function initTrack(track) {
		var half = 0;
		var offset = 0;
		var speed = 0;                 // px per second
		var dragging = false;
		var hovering = false;
		var pointerStartX = 0;
		var offsetAtDragStart = 0;
		var lastFrame = null;

		// Derive the scroll speed from the CSS animation duration *before* we
		// disable it, so the declared duration stays the single source of truth.
		var declaredDuration = parseFloat(getComputedStyle(track).animationDuration) || 60;

		function measure() {
			half = track.scrollWidth / 2;
			speed = half > 0 ? half / declaredDuration : 0;
			wrap();
			apply();
		}

		function wrap() {
			if (half <= 0) { return; }
			while (offset <= -half) { offset += half; }
			while (offset > 0) { offset -= half; }
		}

		function apply() {
			track.style.transform = 'translateX(' + offset + 'px)';
		}

		function frame(now) {
			if (lastFrame === null) { lastFrame = now; }
			var dt = (now - lastFrame) / 1000;
			lastFrame = now;
			if (dt > 0.25) { dt = 0.25; }          // ignore background-tab jumps
			if (!dragging && !hovering && !reduceMotion) {
				offset -= speed * dt;
				wrap();
				apply();
			}
			window.requestAnimationFrame(frame);
		}

		function onPointerDown(e) {
			if (e.button != null && e.button !== 0) { return; }
			dragging = true;
			pointerStartX = e.clientX;
			offsetAtDragStart = offset;
			track.classList.add('is-dragging');
			if (track.setPointerCapture) {
				try { track.setPointerCapture(e.pointerId); } catch (err) { /* no-op */ }
			}
		}

		function onPointerMove(e) {
			if (!dragging) { return; }
			offset = offsetAtDragStart + (e.clientX - pointerStartX);
			wrap();
			apply();
			e.preventDefault();
		}

		function onPointerUp(e) {
			if (!dragging) { return; }
			dragging = false;
			track.classList.remove('is-dragging');
			if (track.releasePointerCapture) {
				try { track.releasePointerCapture(e.pointerId); } catch (err) { /* no-op */ }
			}
		}

		track.classList.add('is-draggable');
		measure();
		window.requestAnimationFrame(frame);

		track.addEventListener('mouseenter', function () { hovering = true; });
		track.addEventListener('mouseleave', function () { hovering = false; });
		track.addEventListener('pointerdown', onPointerDown);
		track.addEventListener('pointermove', onPointerMove);
		track.addEventListener('pointerup', onPointerUp);
		track.addEventListener('pointercancel', onPointerUp);
		track.addEventListener('dragstart', function (e) { e.preventDefault(); });

		window.addEventListener('resize', measure);
		// Widths are unknown until the images decode.
		Array.prototype.forEach.call(track.querySelectorAll('img'), function (img) {
			if (!img.complete) { img.addEventListener('load', measure); }
		});
	}

	function init() {
		Array.prototype.forEach.call(
			document.querySelectorAll('.rolling-gallery'),
			initTrack
		);
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}
}());
