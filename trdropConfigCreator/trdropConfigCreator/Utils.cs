using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace trdropConfigCreator
{
    class Utils
    {
        public static int conformToBounds(int num, int min, int max)
        {
            return Math.Min(Math.Max(num, min), max);
        }

        public static int parseNumber(string numStr, int min, int max)
        {
            bool parsed = int.TryParse(numStr, out int number);
            if (parsed)
                return conformToBounds(number, min, max);
            else
                return 0;
        }
    }
}
