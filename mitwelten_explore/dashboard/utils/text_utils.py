import datetime
import re


def beautify_timedelta(td: datetime.timedelta):
    days = td.days
    if days > 14:
        return f"{int(days/7)} weeks ago"
    elif days > 7:
        return f"{int(days/7)} week ago"
    elif days > 1:
        return f"{days} days ago"
    elif days == 1:
        return "1 day ago"
    else:
        hours = int(td.total_seconds() / 3600)
        if hours > 1:
            return f"{int(hours)} hours ago"
        elif hours == 1:
            return "1 hour ago"
        else:
            minutes = int(td.total_seconds() / 60)
            return f"{minutes} minutes ago"


def markdown_to_plain_text(markdown_text):
    # Remove headers
    markdown_text = re.sub(
        r"^#+\s+(.*?)\s*$", r"\1\n", markdown_text, flags=re.MULTILINE
    )

    # Remove emphasis (bold and italic)
    markdown_text = re.sub(r"(\*{1,2}|_{1,2})(.*?)\1", r"\2", markdown_text)

    # Remove unordered list markers
    markdown_text = re.sub(
        r"^\s*-\s+(.*?)\s*$", r"\1\n", markdown_text, flags=re.MULTILINE
    )

    # Remove ordered list markers
    markdown_text = re.sub(
        r"^\s*\d+\.\s+(.*?)\s*$", r"\1\n", markdown_text, flags=re.MULTILINE
    )

    # Remove horizontal rules
    markdown_text = re.sub(r"^\s*[-*_]{3,}\s*$", "", markdown_text, flags=re.MULTILINE)

    # Remove inline code
    markdown_text = re.sub(r"`{1,2}(.*?)`{1,2}", r"\1", markdown_text)

    # Remove links
    markdown_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", markdown_text)

    # Remove images
    markdown_text = re.sub(r"!\[([^\]]+)\]\([^)]+\)", r"\1", markdown_text)
    return markdown_text.strip()
