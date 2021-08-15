--加入动画

import "android.animation.ObjectAnimator"

local function obj_ani_float(wts,name,from,to)
  for k,v in pairs(wts) do
      local ani = ObjectAnimator.ofFloat(v,name,{from,to})
      ani.setDuration(700)
      ani.start()
  end
end

local function alpha_ani(wts)
  obj_ani_float(wts,"alpha",0,1)
end

local function upmove_ani(wts)
  obj_ani_float(wts,"translationY",100,0)
end

local function scale_ani(wts)
  obj_ani_float(wts,"scaleX",0.3,1)
  obj_ani_float(wts,"scaleY",0.3,1)
end

local function both_ani(wts)
    alpha_ani(wts)
    upmove_ani(wts)
end

local animators = {
  main = function()
    both_ani({btm_lay})
    alpha_ani({top})
    scale_ani({bsIcon})
  end;
  ulpro = function()
    both_ani({desc,swit})
    scale_ani({title})
  end
}

local function getAni(activity)
  --获取动画
  animators[activity]()
end

return getAni;