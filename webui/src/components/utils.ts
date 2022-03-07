import { BlockTree, isBlock } from "../data-model/blocks";

export const createGridKey = (child: BlockTree, idx: number): string => {
  /**
   * Plot blocks - `refId` is a randomly generated uuid to force remount when the document changes, as plots don't always respond to layout changes
   * Other non-layout blocks - `refId` is the hash of the element, so the block remounts whenever the element changes
   * Layout blocks - the key doesn't matter as long as it's unique, as our layout blocks don't hold state
   *
   * Note that indexes are used so that duplicate blocks on the same level have unique keys
   *
   * TODO - We may want to revisit this approach as using hashes causes blocks to remount on content change,
   *        and using indexes means we need to be careful to clear block state whenever props change.
   *        The approach recommended by React is to use BE-generated keys, but this isn't a straightforward solution here
   *        as we'd need a solution that doesn't involve the user maintaining their own keys in the editor
   */
  return isBlock(child) ? `${child.refId}-${idx}` : `${child.name}-${idx}`;
};
