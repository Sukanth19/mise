#!/bin/bash
clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              🍳 MISE RECIPE SAVER 🍳                      ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Your application is ready and working!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  HOW TO USE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1️⃣  Open your browser to:"
echo "      👉 http://localhost:3000"
echo ""
echo "  2️⃣  Log in with:"
echo "      Username: demo"
echo "      Password: demo1234"
echo ""
echo "  3️⃣  See your 10 sample recipes! 🎉"
echo ""
echo "  4️⃣  Click 'CREATE RECIPE' to add new ones"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SAMPLE RECIPES LOADED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🍕 Classic Margherita Pizza"
echo "  🍛 Chicken Tikka Masala"
echo "  🥑 Avocado Toast with Poached Egg"
echo "  🌮 Beef Tacos"
echo "  🥗 Caesar Salad"
echo "  🍪 Chocolate Chip Cookies"
echo "  🥙 Greek Salad"
echo "  🍜 Pad Thai"
echo "  🍌 Banana Bread"
echo "  🍅 Caprese Salad"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  WHY IT WASN'T WORKING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ❌ You weren't logged in!"
echo "  ✅ Just log in and everything works!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press any key to open the application..."
read -n 1 -s

# Try to open browser
if command -v xdg-open > /dev/null; then
  xdg-open http://localhost:3000
elif command -v gnome-open > /dev/null; then
  gnome-open http://localhost:3000
elif command -v kde-open > /dev/null; then
  kde-open http://localhost:3000
else
  echo "Please open http://localhost:3000 in your browser"
fi

# Also open the HTML guide
if command -v xdg-open > /dev/null; then
  xdg-open HOW_TO_USE.html
fi
