import argparse
import json
from pathlib import Path

from . import file_scanner, msg_viewer, path_validator, project_manager, workcopy_creator
from . import res_inventory as res_inv
from .glossary_manager import GlossaryManager
from .translation_schema import TranslationCorpus


def _corpus_path(root: Path) -> Path:
    return root / "translation_corpus.json"


def _cmd_project_init(args):
    config = project_manager.create_project(
        root=Path(args.root),
        original_source_path=Path(args.original_source),
        workcopy_path=Path(args.workcopy),
        backup_path=Path(args.backup),
        output_path=Path(args.output),
    )
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))


def _cmd_validate_path(args):
    result = path_validator.validate_game_root(Path(args.game_root))
    print(json.dumps({
        "game_root": str(result.game_root),
        "ok": result.ok,
        "msg_dir_found": result.msg_dir_found,
        "res_dir_found": result.res_dir_found,
        "grp_dir_found": result.grp_dir_found,
        "warnings": result.warnings,
    }, indent=2, ensure_ascii=False))


def _cmd_scan(args):
    config = project_manager.load_project(Path(args.root))
    results = file_scanner.scan_directory(config.original_source_path)
    report = file_scanner.write_scan_report(results, config.root / "reports")
    print(json.dumps(
        {"file_count": report["file_count"], "json": str(report["json"]), "csv": str(report["csv"])},
        indent=2, ensure_ascii=False,
    ))


def _cmd_make_workcopy(args):
    config = project_manager.load_project(Path(args.root))
    path = workcopy_creator.make_workcopy(
        config.original_source_path, config.workcopy_path, allow_existing=args.allow_existing,
    )
    print(json.dumps({"workcopy_path": str(path)}, indent=2, ensure_ascii=False))


def _cmd_res_inventory(args):
    config = project_manager.load_project(Path(args.root))
    results = res_inv.inventory_res_folder(Path(args.res_path))
    out_path = res_inv.write_res_inventory(results, config.root / "reports" / "res_inventory.json")
    print(json.dumps({"file_count": len(results), "output": str(out_path)}, indent=2, ensure_ascii=False))


def _cmd_glossary_add(args):
    config = project_manager.load_project(Path(args.root))
    glossary_path = config.root / "glossary.json"
    manager = GlossaryManager.load(glossary_path)
    entry = manager.add(args.ja, args.ko, category=args.category)
    manager.save(glossary_path)
    print(json.dumps(entry.to_dict(), indent=2, ensure_ascii=False))


def _cmd_corpus_status(args):
    config = project_manager.load_project(Path(args.root))
    corpus = TranslationCorpus.load(_corpus_path(config.root))
    print(json.dumps(corpus.status_counts(), indent=2, ensure_ascii=False))


def _cmd_msg_inspect(args):
    container = msg_viewer.read_n11f_container(Path(args.file))
    result = {
        "path": str(container.path),
        "pointer_table_offset": container.pointer_table_offset,
        "boundary_marker": container.boundary_marker.hex(),
        "text_length": len(container.text_bytes),
        "pointer_count": len(container.pointer_table_bytes) // 4,
    }
    if args.find_strings:
        result["msg_tag_candidates"] = msg_viewer.find_msg_tag_candidates(container.text_decoded)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def _cmd_status(args):
    config = project_manager.load_project(Path(args.root))
    corpus = TranslationCorpus.load(_corpus_path(config.root))
    print(json.dumps({
        "project_root": str(config.root),
        "original_source_path": str(config.original_source_path),
        "workcopy_path": str(config.workcopy_path),
        "workcopy_exists": config.workcopy_path.exists(),
        "translation_status_counts": corpus.status_counts(),
    }, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="localizer")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("project-init")
    p.add_argument("--root", required=True)
    p.add_argument("--original-source", required=True)
    p.add_argument("--workcopy", required=True)
    p.add_argument("--backup", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=_cmd_project_init)

    p = sub.add_parser("validate-path")
    p.add_argument("--game-root", required=True)
    p.set_defaults(func=_cmd_validate_path)

    p = sub.add_parser("scan")
    p.add_argument("--root", required=True)
    p.set_defaults(func=_cmd_scan)

    p = sub.add_parser("make-workcopy")
    p.add_argument("--root", required=True)
    p.add_argument("--allow-existing", action="store_true")
    p.set_defaults(func=_cmd_make_workcopy)

    p = sub.add_parser("res-inventory")
    p.add_argument("--root", required=True)
    p.add_argument("--res-path", required=True)
    p.set_defaults(func=_cmd_res_inventory)

    p = sub.add_parser("glossary-add")
    p.add_argument("--root", required=True)
    p.add_argument("--ja", required=True)
    p.add_argument("--ko", required=True)
    p.add_argument("--category", default=None)
    p.set_defaults(func=_cmd_glossary_add)

    p = sub.add_parser("corpus-status")
    p.add_argument("--root", required=True)
    p.set_defaults(func=_cmd_corpus_status)

    p = sub.add_parser("msg-inspect")
    p.add_argument("--file", required=True)
    p.add_argument("--find-strings", action="store_true")
    p.add_argument("--min-len", type=int, default=4)
    p.set_defaults(func=_cmd_msg_inspect)

    p = sub.add_parser("status")
    p.add_argument("--root", required=True)
    p.set_defaults(func=_cmd_status)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
