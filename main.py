import click
import parser


@click.command()
@click.argument('DIR')
def main(dir):
    """Load [Fog of World] data from DIR.

    DIR is the path to the [Fog of World] folder, the given folder should contain a subfolder [Sync].
    """
    fog_map = parser.FogMap(dir)



if __name__ == "__main__":
    main()
