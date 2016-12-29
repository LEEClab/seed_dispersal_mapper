###########################################################
#
# Generating and exploring seed rain functions
#  Seed dispersal chance vs distance to fragments
#  which varies with fragment size
#
# Bernardo Niebuhr
# John Ribeiro
# Flavia Pinto
# Milton Ribeiro
#
# Dec. 2016
###########################################################

##############################
# Testing Weibull and exponential curves

par(mfrow=c(3,1))
curve(dweibull(x, shape=2, scale = 250), 0, 1500, xlab = "", ylab = "")
curve(dweibull(x, shape=2, scale = 500), 0, 1500, xlab = "", ylab = "")
curve(dweibull(x, shape=2, scale = 1000), 0, 1500, xlab = "", ylab = "")

curve(dweibull(x, shape=1, scale = 250), 0, 1500, xlab = "", ylab = "")
curve(dweibull(x, shape=1, scale = 500), 0, 1500, xlab = "", ylab = "")
curve(dweibull(x, shape=1, scale = 1000), 0, 1500, xlab = "", ylab = "")
par(mfrow=c(1,1))

# fragments > 250ha
# limit distance = 1000m
350*dweibull(1000, shape=1, scale = 350)
curve(350*dweibull(x, shape=1, scale = 350),0, 1500, col = 1, lwd = 2, lty = 1, 
      #ylab = "Chance de deposição de sementes", xlab = "Distâcia da borda do fragmento (m)")
      ylab = "Seed dispersal chance", xlab = "Distance from habitat patch edge (m)")
# equals to:
#curve(350*dexp(x, rate = 1/350), add=T, col = 2, lty = 2, lwd = 2)

# fragments 50 - 250ha
# limit distance = 850m
200*dweibull(750, shape=1, scale = 290)
290*dweibull(850, shape=1, scale = 290)
curve(290*dweibull(x, shape=1, scale = 290), 0, 1500, add=T, lty = 1, col = 2, lwd = 2)

# fragmentos 25 - 50ha
# limit distance 650m
120*dweibull(500, shape=1, scale = 220)
220*dweibull(650, shape=1, scale = 220)
curve(220*dweibull(x, shape=1, scale = 220), 0, 1500, add=T, lty = 1, col = 3, lwd = 2)

# fragments 10 - 25ha
# limit distance 500m
70*dweibull(350, shape=1, scale = 170)
170*dweibull(500, shape=1, scale = 170)
curve(170*dweibull(x, shape=1, scale = 170), 0, 1500, add=T, lty = 1, col = 4, lwd = 2)

# fragments < 10ha
# limit distance 350m
30*dweibull(200, shape=1, scale = 130)
130*dweibull(350, shape=1, scale = 130)
curve(130*dweibull(x, shape=1, scale = 130), 0, 1500, add=T, lty = 1, col = 6, lwd = 2)

legend("topright", legend = c("< 10ha", "10 - 25ha", "25 - 50ha", "50 - 250ha", "> 250ha"), col = c(6, 4, 3, 2, 1),
      # lwd = 2, title = "Tamanho do fragmento", bty = "n")
      lwd = 2, title = "Patch size", bty = "n")

##############################
# Testing Logistic curves

# Logistic function has three parameters:
# K: the maximum value of the curve, here when x = 0 (for the seed dispersal model, it should be always = 1)
# r: the rate of decrease as x increases (steepness of the curve)
# a: the x value at the sigmoid mid-point (when the function value is K/2)
logistic <- function(x, K, r, a)
{
  K/(1 + exp(r*(x - a)))
}

plot(0, 0, type = 'n', xlim = c(0, 1500), ylim = c(0,1), 
     ylab = "Seed dispersal chance", xlab = "Distance from habitat patch edge (m)")

abline(h = 0.5, lty=2, col = "grey")
abline(v = c(150, 200, 300, 400, 500), lty=2, col = "grey")

curve(logistic(x, 1, 1/100, 500), from = 0, to = 1500, ylim = c(0,1), add = T, lwd = 2)
curve(logistic(x, 1, 1/80, 400), from = 0, to = 1500, ylim = c(0,1), add=T, col = 2, lwd = 2)
curve(logistic(x, 1, 1/60, 300), from = 0, to = 1500, ylim = c(0,1), add=T, col = 3, lwd = 2)
curve(logistic(x, 1, 1/40, 200), from = 0, to = 1500, ylim = c(0,1), add=T, col = 4, lwd = 2)
curve(logistic(x, 1, 1/30, 150), from = 0, to = 1500, ylim = c(0,1), add=T, col = 6, lwd = 2)

legend("topright", legend = c("< 10ha", "10 - 25ha", "25 - 50ha", "50 - 250ha", "> 250ha"), col = c(6, 4, 3, 2, 1),
       #lwd = 2, title = "Tamanho do fragmento", bty = "n")
       lwd = 2, title = "Patch size", bty = "n")
