"""
Shotstack Editing actions - High-level convenience actions for video editing.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

try:
    from shotstack.shotstack import shotstack
    from shotstack.helpers import (
        EDIT_API_BASE,
        get_environment,
        get_headers,
        poll_render_until_complete,
        get_media_info,
        position_to_offset,
        build_timeline_from_clips,
    )
except ImportError:
    from shotstack import shotstack
    from helpers import (
        EDIT_API_BASE,
        get_environment,
        get_headers,
        poll_render_until_complete,
        get_media_info,
        position_to_offset,
        build_timeline_from_clips,
    )


@shotstack.action("custom_edit")
class CustomEditAction(ActionHandler):
    """Create a fully customizable video edit using Shotstack's timeline structure."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            wait_for_completion = inputs.get("wait_for_completion", True)
            max_wait = inputs.get("max_wait_seconds", 300)

            payload = {
                "timeline": inputs["timeline"],
                "output": inputs["output"]
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            if wait_for_completion:
                poll_result = await poll_render_until_complete(context, render_id, max_wait)

                if poll_result["status"] == "done":
                    render_data = poll_result.get("render", {})
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": "done",
                            "url": poll_result["url"],
                            "duration": render_data.get("duration"),
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "queued",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("compose_video")
class ComposeVideoAction(ActionHandler):
    """Combine multiple video/image clips with transitions."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            clips = inputs["clips"]
            output = inputs.get("output", {"format": "mp4", "resolution": "hd"})
            background_color = inputs.get("background_color", "#000000")
            wait_for_completion = inputs.get("wait_for_completion", True)

            timeline = build_timeline_from_clips(clips, background_color)

            payload = {
                "timeline": timeline,
                "output": output
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            if wait_for_completion:
                poll_result = await poll_render_until_complete(context, render_id)

                if poll_result["status"] == "done":
                    render_data = poll_result.get("render", {})
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": "done",
                            "url": poll_result["url"],
                            "duration": render_data.get("duration"),
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "queued",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("add_text_overlay")
class AddTextOverlayAction(ActionHandler):
    """Add text/titles to a video at specified time and position."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            video_url = inputs["video_url"]
            text = inputs["text"]
            style = inputs.get("style", "minimal")
            position = inputs.get("position", "center")
            start_time = inputs.get("start_time", 0)
            duration = inputs.get("duration")
            font_size = inputs.get("font_size", "medium")
            color = inputs.get("color", "#ffffff")
            background_color = inputs.get("background_color")
            effect = inputs.get("effect")
            transition = inputs.get("transition")
            output = inputs.get("output", {"format": "mp4", "resolution": "hd"})
            wait_for_completion = inputs.get("wait_for_completion", True)

            if not duration:
                try:
                    media_info = await get_media_info(context, video_url)
                    video_duration = media_info.get("metadata", {}).get("streams", [{}])[0].get("duration", 10)
                    duration = video_duration - start_time
                except Exception:
                    duration = 10

            title_asset = {
                "type": "title",
                "text": text,
                "style": style,
                "color": color,
                "size": font_size,
                "position": position
            }
            if background_color:
                title_asset["background"] = background_color

            text_clip = {
                "asset": title_asset,
                "start": start_time,
                "length": duration
            }
            if effect:
                text_clip["effect"] = effect
            if transition:
                text_clip["transition"] = transition

            video_clip = {
                "asset": {"type": "video", "src": video_url},
                "start": 0
            }

            timeline = {
                "tracks": [
                    {"clips": [text_clip]},
                    {"clips": [video_clip]}
                ]
            }

            payload = {
                "timeline": timeline,
                "output": output
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            if wait_for_completion:
                poll_result = await poll_render_until_complete(context, render_id)

                if poll_result["status"] == "done":
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": "done",
                            "url": poll_result["url"],
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "queued",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("add_logo_overlay")
class AddLogoOverlayAction(ActionHandler):
    """Add logo/watermark to a video."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            video_url = inputs["video_url"]
            logo_url = inputs["logo_url"]
            position = inputs.get("position", "bottomRight")
            scale = inputs.get("scale", 0.15)
            opacity = inputs.get("opacity", 1)
            offset_x = inputs.get("offset_x")
            offset_y = inputs.get("offset_y")
            start_time = inputs.get("start_time", 0)
            duration = inputs.get("duration")
            output = inputs.get("output", {"format": "mp4", "resolution": "hd"})
            wait_for_completion = inputs.get("wait_for_completion", True)

            if not duration:
                try:
                    media_info = await get_media_info(context, video_url)
                    video_duration = media_info.get("metadata", {}).get("streams", [{}])[0].get("duration", 10)
                    duration = video_duration - start_time
                except Exception:
                    duration = 10

            logo_clip = {
                "asset": {"type": "image", "src": logo_url},
                "start": start_time,
                "length": duration,
                "scale": scale,
                "position": position,
                "opacity": opacity
            }

            if offset_x is not None or offset_y is not None:
                offset = position_to_offset(position)
                if offset_x is not None:
                    offset["x"] = offset_x
                if offset_y is not None:
                    offset["y"] = offset_y
                logo_clip["offset"] = offset

            video_clip = {
                "asset": {"type": "video", "src": video_url},
                "start": 0
            }

            timeline = {
                "tracks": [
                    {"clips": [logo_clip]},
                    {"clips": [video_clip]}
                ]
            }

            payload = {
                "timeline": timeline,
                "output": output
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            if wait_for_completion:
                poll_result = await poll_render_until_complete(context, render_id)

                if poll_result["status"] == "done":
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": "done",
                            "url": poll_result["url"],
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "queued",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("add_audio_track")
class AddAudioTrackAction(ActionHandler):
    """Add background music or voiceover to a video."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            video_url = inputs["video_url"]
            audio_url = inputs["audio_url"]
            volume = inputs.get("volume", 1)
            start_time = inputs.get("start_time", 0)
            trim_from = inputs.get("trim_from", 0)
            trim_duration = inputs.get("trim_duration")
            fade_in = inputs.get("fade_in")
            fade_out = inputs.get("fade_out")
            mix_mode = inputs.get("mix_mode", "mix")
            output = inputs.get("output", {"format": "mp4", "resolution": "hd"})
            wait_for_completion = inputs.get("wait_for_completion", True)

            video_asset = {"type": "video", "src": video_url}
            if mix_mode == "replace":
                video_asset["volume"] = 0

            video_clip = {
                "asset": video_asset,
                "start": 0
            }

            audio_asset = {
                "type": "audio",
                "src": audio_url,
                "volume": volume
            }
            if trim_from:
                audio_asset["trim"] = trim_from

            if fade_in and fade_out:
                audio_asset["effect"] = "fadeInFadeOut"
            elif fade_in:
                audio_asset["effect"] = "fadeIn"
            elif fade_out:
                audio_asset["effect"] = "fadeOut"

            audio_clip = {
                "asset": audio_asset,
                "start": start_time
            }
            if trim_duration:
                audio_clip["length"] = trim_duration

            timeline = {
                "tracks": [
                    {"clips": [video_clip]},
                    {"clips": [audio_clip]}
                ]
            }

            payload = {
                "timeline": timeline,
                "output": output
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            if wait_for_completion:
                poll_result = await poll_render_until_complete(context, render_id)

                if poll_result["status"] == "done":
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": "done",
                            "url": poll_result["url"],
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "queued",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("trim_video")
class TrimVideoAction(ActionHandler):
    """Extract a segment from a video."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            video_url = inputs["video_url"]
            start_time = inputs["start_time"]
            end_time = inputs.get("end_time")
            duration = inputs.get("duration")
            output = inputs.get("output", {"format": "mp4", "resolution": "hd"})
            wait_for_completion = inputs.get("wait_for_completion", True)

            if end_time is not None:
                length = end_time - start_time
            elif duration is not None:
                length = duration
            else:
                return ActionResult(
                    data={"result": False, "error": "Either end_time or duration is required"},
                    cost_usd=0.0
                )

            video_clip = {
                "asset": {
                    "type": "video",
                    "src": video_url,
                    "trim": start_time
                },
                "start": 0,
                "length": length
            }

            timeline = {
                "tracks": [{"clips": [video_clip]}]
            }

            payload = {
                "timeline": timeline,
                "output": output
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            if wait_for_completion:
                poll_result = await poll_render_until_complete(context, render_id)

                if poll_result["status"] == "done":
                    render_data = poll_result.get("render", {})
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": "done",
                            "url": poll_result["url"],
                            "duration": render_data.get("duration"),
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "queued",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("concatenate_videos")
class ConcatenateVideosAction(ActionHandler):
    """Join multiple videos sequentially."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            videos = inputs["videos"]
            transition = inputs.get("transition")
            output = inputs.get("output", {"format": "mp4", "resolution": "hd"})
            wait_for_completion = inputs.get("wait_for_completion", True)

            clips = []
            for i, video_url in enumerate(videos):
                video_clip = {
                    "asset": {"type": "video", "src": video_url},
                    "start": 0
                }

                if transition and transition != "none":
                    trans = {}
                    if i > 0:
                        trans["in"] = transition
                    if i < len(videos) - 1:
                        trans["out"] = transition
                    if trans:
                        video_clip["transition"] = trans

                clips.append(video_clip)

            timeline = {
                "tracks": [{"clips": clips}]
            }

            payload = {
                "timeline": timeline,
                "output": output
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            if wait_for_completion:
                poll_result = await poll_render_until_complete(context, render_id)

                if poll_result["status"] == "done":
                    render_data = poll_result.get("render", {})
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": "done",
                            "url": poll_result["url"],
                            "duration": render_data.get("duration"),
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "queued",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("add_captions")
class AddCaptionsAction(ActionHandler):
    """Add auto-generated or manual captions/subtitles to a video with customizable styling."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            video_url = inputs["video_url"]

            # Caption source - either auto-generate or use provided SRT/VTT
            subtitle_url = inputs.get("subtitle_url")  # URL to SRT/VTT file
            auto_generate = inputs.get("auto_generate", True)  # Auto-generate from audio

            # Font styling
            font_family = inputs.get("font_family")  # e.g., "Open Sans", "Roboto"
            font_size = inputs.get("font_size", 16)  # Font size in pixels
            font_color = inputs.get("font_color", "#ffffff")  # Text color
            line_height = inputs.get("line_height")  # Line spacing
            stroke_color = inputs.get("stroke_color")  # Text outline color
            stroke_width = inputs.get("stroke_width")  # Text outline width

            # Background styling
            background_color = inputs.get("background_color")  # e.g., "#000000"
            background_opacity = inputs.get("background_opacity", 0.8)  # 0-1
            background_padding = inputs.get("background_padding", 10)  # Padding in pixels
            background_border_radius = inputs.get("background_border_radius", 4)  # Corner radius

            # Position and margins
            position = inputs.get("position", "bottom")  # top, bottom, center
            margin_top = inputs.get("margin_top")
            margin_bottom = inputs.get("margin_bottom", 0.1)  # Default slight margin from bottom
            margin_left = inputs.get("margin_left")
            margin_right = inputs.get("margin_right")

            # Caption dimensions
            caption_width = inputs.get("width")  # Caption box width
            caption_height = inputs.get("height")  # Caption box height

            output = inputs.get("output", {"format": "mp4", "resolution": "hd"})
            wait_for_completion = inputs.get("wait_for_completion", True)
            max_wait = inputs.get("max_wait_seconds", 300)

            # Build video clip with alias for auto-caption reference
            video_clip = {
                "asset": {"type": "video", "src": video_url},
                "start": 0,
                "length": "auto"
            }

            # Add alias if auto-generating captions
            if auto_generate and not subtitle_url:
                video_clip["alias"] = "main_video"

            # Build caption asset
            caption_asset = {
                "type": "caption"
            }

            # Set caption source
            if subtitle_url:
                caption_asset["src"] = subtitle_url
            elif auto_generate:
                caption_asset["src"] = "alias://main_video"
            else:
                return ActionResult(
                    data={"result": False, "error": "Either subtitle_url or auto_generate=True is required"},
                    cost_usd=0.0
                )

            # Build font object if any font properties are set
            font = {}
            if font_family:
                font["family"] = font_family
            if font_size:
                font["size"] = font_size
            if font_color:
                font["color"] = font_color
            if line_height:
                font["lineHeight"] = line_height
            if stroke_color:
                font["stroke"] = stroke_color
            if stroke_width:
                font["strokeWidth"] = stroke_width

            if font:
                caption_asset["font"] = font

            # Build background object if any background properties are set
            if background_color:
                background = {
                    "color": background_color
                }
                if background_opacity is not None:
                    background["opacity"] = background_opacity
                if background_padding is not None:
                    background["padding"] = background_padding
                if background_border_radius is not None:
                    background["borderRadius"] = background_border_radius
                caption_asset["background"] = background

            # Set position
            if position:
                caption_asset["position"] = position

            # Build margin object if any margins are set
            margin = {}
            if margin_top is not None:
                margin["top"] = margin_top
            if margin_bottom is not None:
                margin["bottom"] = margin_bottom
            if margin_left is not None:
                margin["left"] = margin_left
            if margin_right is not None:
                margin["right"] = margin_right

            if margin:
                caption_asset["margin"] = margin

            # Set dimensions if provided
            if caption_width:
                caption_asset["width"] = caption_width
            if caption_height:
                caption_asset["height"] = caption_height

            # Build caption clip
            caption_clip = {
                "asset": caption_asset,
                "start": 0,
                "length": "end"
            }

            # Build timeline with captions on top track
            timeline = {
                "tracks": [
                    {"clips": [caption_clip]},
                    {"clips": [video_clip]}
                ]
            }

            payload = {
                "timeline": timeline,
                "output": output
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            if wait_for_completion:
                poll_result = await poll_render_until_complete(context, render_id, max_wait)

                if poll_result["status"] == "done":
                    render_data = poll_result.get("render", {})
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": "done",
                            "url": poll_result["url"],
                            "duration": render_data.get("duration"),
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "render_id": render_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "queued",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )
