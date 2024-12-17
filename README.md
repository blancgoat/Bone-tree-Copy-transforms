# Bone-tree-Copy-transforms

Note! Don't forget Blender's vanilla feature, 'Bone Relative'.  
This might actually be the feature you're looking for in most cases.

There are two armatures. For example, there may be a body and clothes.  
The clothes are designed to be compatible with the body, and they share the same structure and bone names.  
If your need is to apply Copy Transforms to all bones at once, you can use this add-on. 

## Example
![image](https://github.com/user-attachments/assets/61354ddd-9e36-4ab1-8aa2-7bce2fb283d5)
Body: Player01  
Clothes: Captain_clo

![Untitled-1](https://github.com/user-attachments/assets/2003469b-440e-4e2c-bc23-d333d66062eb)
The two armatures have almost identical structures based on Skl_Root.

![image](https://github.com/user-attachments/assets/596a567a-eeb4-45ac-9400-d48a03de0236)
Proceed as shown in the image above.

![SHANA 화면 녹화 중 2024-12-17 162433](https://github.com/user-attachments/assets/454dab58-ea09-40ec-99ee-8895fa9b8ee6)
and job done.


#### Traversal Mode
- Parent-based: Traverses bones based on the parent. Choose this if the armatures are perfectly compatible.
- Child-based: Traverses bones based on the child. Choose this if the bone structures differ but the bone names match. However, this may cause malfunctions.

