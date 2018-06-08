"""Functionality related to offline rendering of a Sequence Node tree"""

from collections import deque

# Script role to trigger during the breadth-first rendering pass.
RENDER_BFS_ROLE = 'render.bfs'

# Script role to trigger during the depth-first rendering pass, before the current node's descendants are rendered.
RENDER_DFS_START_ROLE = 'render.dfs_start'

# Script role to trigger during the depth-first rendering pass, after the current node's descendants have been rendered.
RENDER_DFS_END_ROLE = 'render.dfs.end'

def render_subtree(node, detach=False):
  """Renders a Sequence Node (sub)tree by calling the user-defined rendering scripts.
  Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
  gracefully.
  node -- Root of the subtree to render.
  detach -- Boolean indicating whether to detach the subtree root from its parent during rendering (true) or not
    (false). Has no effect if the subtree root has no parent, i.e. the subtree is the whole tree.
  """
  # Detach node from parent if appropriate.
  parent = node.parent
  if parent is not None and detach:
    node.parent.remove_child(node.name)
  
  # Get a reference to the tree root so we don't recompute it over and over. (root should be the same as node if detach
  # is true.)
  root = node.root_ancestor()
  env = {}
  
  # Perform the breadth-first pass.
  _render_subtree_bfs(node, root, env)
  
  # Perform the depth-first pass.
  _render_subtree_dfs(node, root, env)
  
  # Reattach the node to its parent if appropriate.
  if parent is not None and detach:
    node.parent.add_child(node)

def _render_subtree_bfs(node, root, env):
  """Performs the breadth-first pass of rendering a Sequence Node subtree.
  node -- Root of the subtree to render.
  root -- Root of the whole tree; might be used by scripts.
  env -- Environment dictionary to pass to scripts. Scripts can modify this dictionary to compute data for later
    scripts.
  """
  bfs_frontier = deque([node])
  
  while len(bfs_frontier) > 0:
    # Call the script on the next node.
    next_node = bfs_frontier.popleft()
    next_node.call_script(RENDER_BFS_ROLE, root, env)
    
    # Sort children by starting horizontal position, and add them to the queue.
    children = next_node.sorted_children()
    bfs_frontier.extend(children)

def _render_subtree_dfs(node, root, env):
  """Performs the depth-first pass of rendering a Sequence Node subtree.
  node -- Root of the subtree to render.
  root -- Root of the whole tree; might be used by scripts.
  env -- Environment dictionary to pass to scripts. Scripts can modify this dictionary to compute data for later
    scripts.
  """
  # Call DFS start script.
  node.call_script(RENDER_DFS_START_ROLE, root, env)
  
  # Render children.
  children = node.sorted_children()
  for child in children:
    _render_subtree_dfs(child, root, env)
  
  # Call DFS end script.
  node.call_script(RENDER_DFS_END_ROLE, root, env)
