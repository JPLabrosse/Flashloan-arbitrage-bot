// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Dex is Ownable {
    // Event declarations for logging activities
    event TokenAdded(address token); // Event for adding a token
    event TokenRemoved(address token); // Event for removing a token
    event Deposit(address indexed token, address indexed user, uint amount); // Event for depositing tokens
    event Withdraw(address indexed token, address indexed user, uint amount); // Event for withdrawing tokens

    // Mapping from token addresses to their status in the DEX
    mapping(address => bool) public supportedTokens; // Mapping to check if a token is supported

    // Mapping from user and token to balance
    mapping(address => mapping(address => uint256)) public balances; // Mapping to store user balances for each token

    // Add a token to the list of supported tokens
    function addToken(address token) public onlyOwner {
        require(token != address(0), "Invalid token address"); // Check if the token address is valid
        require(!supportedTokens[token], "Token already added"); // Check if the token is already added
        supportedTokens[token] = true; // Set the token as supported
        emit TokenAdded(token); // Emit the TokenAdded event
    }

    // Remove a token from the list of supported tokens
    function removeToken(address token) public onlyOwner {
        require(supportedTokens[token], "Token not supported"); // Check if the token is supported
        supportedTokens[token] = false; // Set the token as not supported
        emit TokenRemoved(token); // Emit the TokenRemoved event
    }

    // Deposit tokens into the DEX
    function deposit(address token, uint256 amount) public {
        require(supportedTokens[token], "Token not supported"); // Check if the token is supported
        require(amount > 0, "Deposit amount must be greater than zero"); // Check if the deposit amount is greater than zero
        
        IERC20(token).transferFrom(msg.sender, address(this), amount); // Transfer tokens from the user to the DEX
        balances[token][msg.sender] += amount; // Update the user's balance for the token
        emit Deposit(token, msg.sender, amount); // Emit the Deposit event
    }

    // Withdraw tokens from the DEX
    function withdraw(address token, uint256 amount) public {
        require(supportedTokens[token], "Token not supported"); // Check if the token is supported
        require(balances[token][msg.sender] >= amount, "Insufficient balance"); // Check if the user has enough balance
        
        balances[token][msg.sender] -= amount; // Update the user's balance for the token
        IERC20(token).transfer(msg.sender, amount); // Transfer tokens from the DEX to the user
        emit Withdraw(token, msg.sender, amount); // Emit the Withdraw event
    }

    // Function to check the balance of a user for a specific token
    function getBalance(address token, address user) public view returns (uint256) {
        return balances[token][user]; // Return the user's balance for the token
    }
}
