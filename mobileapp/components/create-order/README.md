# Create Order Components Structure

This directory contains modular components for the Create Order screen. Here's the planned component structure:

## Components

1. BusinessSelector
   - Handles ZID selection
   - Manages business selection drawer

2. CustomerSelector
   - Manages customer selection
   - Handles customer search and infinite scroll
   - Customer selection drawer

3. ItemSelector
   - Handles item selection
   - Manages item search and infinite scroll
   - Item selection drawer

4. QuantityInput
   - Quantity input field
   - Validation logic

5. CartItem
   - Individual cart item display
   - Remove item functionality

6. CartList
   - Cart items container
   - Total calculation
   - Cart header with customer info

7. OrderActions
   - Add to cart button
   - Add order button
   - Button state management

## Implementation Steps

1. Create individual component files
2. Extract logic and UI from create-order.jsx
3. Implement state management and data flow
4. Update create-order.jsx to use new components
5. Test and verify functionality

## State Management

- Use React Context for global state if needed
- Implement proper prop drilling
- Maintain cart state in AsyncStorage