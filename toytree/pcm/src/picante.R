

Kcalc <- function(x,phy, checkdata=TRUE) {

    if (checkdata) {
        dat <- match.phylo.data(phy, x)
        x <- dat$data
        phy <- dat$phy
    }
    dat2 <- data.frame(x=x)
    mat <- vcv.phylo(phy)
    dat2$vars <- diag(mat)
    matc <- vcv.phylo(phy, corr=TRUE) # correlation matrix
    ntax <- length(phy$tip.label)

    # calculate "phylogenetic" mean via gls
    fit <- gls(
        x ~ 1, 
        correlation=corSymm(matc[lower.tri(matc)], fixed=TRUE), 
        weights=varFixed(~vars),
        data=dat2,
    )
    ahat <- coef(fit)
    
    #observed
    MSE <- fit$sigma^2
    MSE0 <- t(x-ahat) %*% (x - ahat)/(ntax-1)
    
    #expected
    MSE0.MSE <- 1/(ntax-1) * (sum(diag(mat))-ntax/sum(solve(mat)))
    
    K <- MSE0/MSE / MSE0.MSE
    return(K)

}


pic.variance <- function(x,phy,scaled=TRUE) {
    pics <- pic(x, phy, scaled)
    N <- length(pics)
    sum(pics^2) / (N-1)
}

phylosignal <- function(x, phy, reps=999, checkdata=TRUE, ...) {

    if (checkdata) {
        dat <- match.phylo.data(phy, x)
        x <- dat$data
        phy <- dat$phy
    }
    
    K <- Kcalc(x, phy, checkdata=FALSE)

    if (!is.vector(x)) {
        x.orig <- x
        x <- as.vector(x)
        names(x) <- row.names(x.orig)
    }
    
    obs.var.pic = pic.variance(x,phy,...)
    
    rnd.var.pic <- numeric(reps)
    
    #significance based on tip shuffle
    for (i in 1:reps) {
        tipsh.x <- sample(x)
        names(tipsh.x) <- names(x)
        rnd.var.pic[i] <- pic.variance(tipsh.x,phy,...)
    }

    var.pics = c(obs.var.pic,rnd.var.pic)
    var.pics.p = rank(var.pics)[1] / (reps + 1)
    var.pics.z = (obs.var.pic - mean(var.pics))/sd(var.pics)
    data.frame(K,PIC.variance.obs=obs.var.pic,PIC.variance.rnd.mean=mean(var.pics),PIC.variance.P=var.pics.p, PIC.variance.Z=var.pics.z)

}

multiPhylosignal <- function(x, phy, checkdata=TRUE, ...) {

    if (!(is.data.frame(x) | is.matrix(x))) {
        stop("Expecting trait data in data.frame or matrix format")
    }
    trait <- x[,1]
    names(trait) <- row.names(x)
    pruned <- prune.missing(trait,phy)
    attributes(pruned$data)$na.action<- NULL
    output <- data.frame(phylosignal(pruned$data, pruned$tree, ...))
    if(length(colnames(x))>1) {
        for (i in 2:length(colnames(x))) {
            trait <- x[,i]
            names(trait) <- row.names(x)
            pruned <- prune.missing(trait, phy)
                        attributes(pruned$data)$na.action<- NULL
            output <- rbind(output, phylosignal(pruned$data, pruned$tree, checkdata=FALSE, ...))
        }
    }
    data.frame(output,row.names=colnames(x))
}