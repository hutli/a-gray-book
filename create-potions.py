import re

import click
import httpx

HEADER_REGEX = r"<h1>.*<\/h1>"
HTML_REGEX = r"<[^>]+>"


def clean_html(input):
    return re.sub(HTML_REGEX, "", input)


def create_potion(text):
    [title, text] = text.split("</h2>", 1)
    title = clean_html(title.strip())
    [history, text] = text.strip().split("<ul>", 1)
    history = [clean_html(d.strip()).strip() for d in history.split("</p>")[:-1]]
    return {
        "title": title,
        "history": history,
        **{
            clean_html(t.split(":</b>")[0])
            .strip(): clean_html(t.split(":</b>")[1])
            .strip()
            for t in text.split("</li>")[:-1]
        },
    }


def pp_potion(potion):
    history = "\\\\\\\\".join(potion["history"])
    s = "{"
    e = "}"
    return f"""\potion{s}{potion['title']}{e}{s}
    {potion["Description"]}
{e}{s}{potion['Form']}{e}{s}
    {potion["Roleplaying Effects"]}
{e}{s}
    {potion["Mechanical Effects"]}
{e}{s}
    {potion["Recipe"]}
{e}{s}
    {history}
{e}"""


def pp_chapter(title, description):
    description = "\\\\\\\\".join(description)
    s = "{"
    e = "}"
    return f"""\mychapter{s}{title}{e}{s}
    {description}
{e}"""


@click.command()
@click.option(
    "--input-url",
    "-i",
    required=True,
    type=str,
    help="URL to potions page",
)
def cli(input_url):
    text = httpx.get(input_url).text
    title = text.split("<h1>", 1)[1].split("<", 1)[0].strip()
    content = (
        text.split('id="mw-content-text"', 1)[1]
        .split(">", 1)[1]
        .split('class="printfooter"', 1)[0]
        .rsplit("</div>", 1)[0]
    ).split("<h2>")
    description = [
        clean_html(par.split("</p>", 1)[0].strip()).strip()
        for par in content[0].split("<p>")[1:]
    ]
    potions = [create_potion(p) for p in content[1:]]
    print(
        "\n\n".join([pp_chapter(title, description)] + [pp_potion(p) for p in potions])
    )


if __name__ == "__main__":
    cli()
