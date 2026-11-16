"""Run all three templates with the same input, configuration and cost cohort."""
import subprocess
import sys
from common import HERE, arguments, load_dataset, select_metric_cohort


def main():
    args = arguments('all templates')
    rows, _ = load_dataset(args)
    # Validate the requested cost before emitting a partial batch.
    select_metric_cohort(rows, args.metric, args.missing_cost)
    for name in ['forest', 'raincloud', 'pareto']:
        subprocess.run([sys.executable, str(HERE / f'plot_{name}.py'), *sys.argv[1:]], check=True)
    if 'png' in args.formats:
        from PIL import Image, ImageDraw
        tiles = []
        for name in ['forest', 'raincloud', 'pareto']:
            with Image.open(args.output_dir / f'{name}.png') as im:
                im = im.convert('RGB')
                im.thumbnail((1400, 1000), Image.Resampling.LANCZOS)
                tile = Image.new('RGB', (1440, im.height + 60), 'white')
                tile.paste(im, ((1440 - im.width) // 2, 40))
                ImageDraw.Draw(tile).text((24, 14), name.upper(), fill='#243746')
                tiles.append(tile)
        canvas = Image.new('RGB', (1440, sum(im.height for im in tiles) + 32), '#E6ECEF')
        y = 0
        for tile in tiles:
            canvas.paste(tile, (0, y))
            y += tile.height + 16
        canvas.save(args.output_dir / 'overview.png')
    print('All three templates completed. See *_summary.csv and *_provenance.json beside the figures.')


if __name__ == '__main__':
    main()
